"""
タスク管理API + 障害シミュレーションAPI

目的・理由:
- タスクのCRUD操作を提供
- X-Ray検証用の障害シミュレーションAPIを提供
- すべてのエンドポイントでX-Rayトレーシングを実施

影響範囲:
- タスクデータ（PostgreSQL）
- X-Rayトレース（X-Ray Daemon経由）

前提条件・制約:
- PostgreSQLが稼働していること
- X-Ray Daemonが稼働していること（ECS環境）
"""

import time
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from aws_xray_sdk.core import xray_recorder
from db.postgres import get_db_pool


router = APIRouter(prefix="/tasks", tags=["tasks"])


# --------------------------------
# Pydanticモデル（リクエスト/レスポンス）
# --------------------------------


class TaskCreate(BaseModel):
    """
    タスク作成リクエスト

    目的・理由:
    - POST /tasksのリクエストボディをバリデーション
    - Pydanticで型安全性を担保

    影響範囲:
    - タスク作成API

    前提条件・制約:
    - titleは必須、最大100文字
    - descriptionは任意、最大500文字
    - statusはpending/in_progress/completedのいずれか
    """

    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: str = Field("pending", pattern="^(pending|in_progress|completed)$")


class TaskUpdate(BaseModel):
    """
    タスク更新リクエスト

    目的・理由:
    - PUT /tasks/{id}のリクエストボディをバリデーション
    - 部分更新を許可（すべてのフィールドが任意）

    影響範囲:
    - タスク更新API

    前提条件・制約:
    - すべてのフィールドが任意
    """

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed)$")


class TaskResponse(BaseModel):
    """
    タスクレスポンス

    目的・理由:
    - タスクオブジェクトの標準レスポンス形式
    - ISO 8601形式の日時を保証

    影響範囲:
    - すべてのタスクAPI

    前提条件・制約:
    - idはUUID形式
    - created_at/updated_atはISO 8601形式
    """

    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """
    タスク一覧レスポンス

    目的・理由:
    - タスク一覧のページネーション対応
    - total/limit/offsetでページ情報を提供

    影響範囲:
    - タスク一覧取得API

    前提条件・制約:
    - tasksは空配列を許可
    """

    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int


# --------------------------------
# タスクCRUD操作
# --------------------------------


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> TaskListResponse:
    """
    タスク一覧取得

    目的・理由:
    - タスク一覧をページネーション対応で取得
    - ステータスフィルター機能を提供
    - X-Rayでクエリ実行をトレース

    影響範囲:
    - PostgreSQL（SELECT tasks）
    - X-Rayトレース

    前提条件・制約:
    - limitは1〜100の範囲
    - offsetは0以上
    - status_filterはpending/in_progress/completedのいずれか（任意）
    """
    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL SELECT）
    with xray_recorder.capture("PostgreSQL SELECT tasks"):
        async with pool.acquire() as conn:
            # WHERE句の構築
            where_clause = ""
            params = []
            if status_filter:
                where_clause = "WHERE status = $1"
                params.append(status_filter)
                query = f"SELECT * FROM tasks {where_clause} ORDER BY created_at DESC LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}"
                params.extend([limit, offset])
                count_query = f"SELECT COUNT(*) FROM tasks {where_clause}"
                count_params = [status_filter]
            else:
                query = "SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1 OFFSET $2"
                params = [limit, offset]
                count_query = "SELECT COUNT(*) FROM tasks"
                count_params = []

            # タスク取得
            rows = await conn.fetch(query, *params)
            total = await conn.fetchval(count_query, *count_params)

            # X-Rayメタデータ（実行SQLクエリ）
            xray_recorder.current_subsegment().put_metadata("sql_query", query)

    # レスポンス構築
    tasks = [
        TaskResponse(
            id=str(row["id"]),
            title=row["title"],
            description=row["description"],
            status=row["status"],
            created_at=row["created_at"].isoformat() + "Z",
            updated_at=row["updated_at"].isoformat() + "Z",
        )
        for row in rows
    ]

    return TaskListResponse(tasks=tasks, total=total, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """
    タスク詳細取得

    目的・理由:
    - 指定IDのタスク詳細を取得
    - 存在しない場合は404を返す
    - X-Rayでクエリ実行をトレース

    影響範囲:
    - PostgreSQL（SELECT tasks WHERE id = ?）
    - X-Rayトレース

    前提条件・制約:
    - task_idはUUID形式
    """
    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL SELECT）
    with xray_recorder.capture("PostgreSQL SELECT tasks WHERE id = ?"):
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", uuid.UUID(task_id))

            # X-Rayメタデータ（実行SQLクエリ）
            xray_recorder.current_subsegment().put_metadata(
                "sql_query", f"SELECT * FROM tasks WHERE id = {task_id}"
            )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
        )

    return TaskResponse(
        id=str(row["id"]),
        title=row["title"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"].isoformat() + "Z",
        updated_at=row["updated_at"].isoformat() + "Z",
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate) -> TaskResponse:
    """
    タスク作成

    目的・理由:
    - 新規タスクをDBに登録
    - UUID自動生成、created_at/updated_at自動設定
    - X-Rayでクエリ実行をトレース

    影響範囲:
    - PostgreSQL（INSERT INTO tasks）
    - X-Rayトレース

    前提条件・制約:
    - titleは必須（バリデーション済み）
    """
    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL INSERT）
    with xray_recorder.capture("PostgreSQL INSERT INTO tasks"):
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO tasks (title, description, status)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                task.title,
                task.description,
                task.status,
            )

            # X-Rayメタデータ（実行SQLクエリ）
            xray_recorder.current_subsegment().put_metadata(
                "sql_query", f"INSERT INTO tasks (title={task.title}, status={task.status})"
            )

    return TaskResponse(
        id=str(row["id"]),
        title=row["title"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"].isoformat() + "Z",
        updated_at=row["updated_at"].isoformat() + "Z",
    )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate) -> TaskResponse:
    """
    タスク更新

    目的・理由:
    - 指定IDのタスクを更新
    - 部分更新対応（指定されたフィールドのみ更新）
    - X-Rayでクエリ実行をトレース

    影響範囲:
    - PostgreSQL（UPDATE tasks WHERE id = ?）
    - X-Rayトレース

    前提条件・制約:
    - task_idはUUID形式
    - 存在しないIDの場合は404
    """
    pool = await get_db_pool()

    # 更新フィールドを動的に構築
    updates = []
    params = []
    param_idx = 1

    if task.title is not None:
        updates.append(f"title = ${param_idx}")
        params.append(task.title)
        param_idx += 1

    if task.description is not None:
        updates.append(f"description = ${param_idx}")
        params.append(task.description)
        param_idx += 1

    if task.status is not None:
        updates.append(f"status = ${param_idx}")
        params.append(task.status)
        param_idx += 1

    if not updates:
        # 更新内容がない場合は現在のタスクを返す
        return await get_task(task_id)

    updates.append(f"updated_at = NOW()")
    params.append(uuid.UUID(task_id))

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ${param_idx} RETURNING *"

    # X-Rayサブセグメント（PostgreSQL UPDATE）
    with xray_recorder.capture("PostgreSQL UPDATE tasks WHERE id = ?"):
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)

            # X-Rayメタデータ（実行SQLクエリ）
            xray_recorder.current_subsegment().put_metadata("sql_query", query)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
        )

    return TaskResponse(
        id=str(row["id"]),
        title=row["title"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"].isoformat() + "Z",
        updated_at=row["updated_at"].isoformat() + "Z",
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str) -> None:
    """
    タスク削除

    目的・理由:
    - 指定IDのタスクを削除
    - X-Rayでクエリ実行をトレース

    影響範囲:
    - PostgreSQL（DELETE FROM tasks WHERE id = ?）
    - X-Rayトレース

    前提条件・制約:
    - task_idはUUID形式
    - 存在しないIDの場合は404
    """
    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL DELETE）
    with xray_recorder.capture("PostgreSQL DELETE FROM tasks WHERE id = ?"):
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM tasks WHERE id = $1", uuid.UUID(task_id))

            # X-Rayメタデータ（実行SQLクエリ）
            xray_recorder.current_subsegment().put_metadata(
                "sql_query", f"DELETE FROM tasks WHERE id = {task_id}"
            )

    if result == "DELETE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}},
        )


# --------------------------------
# 障害シミュレーションAPI（X-Ray検証用）
# --------------------------------


@router.get("/slow-db", response_model=dict)
async def slow_db_simulation() -> dict:
    """
    DB遅延シミュレーション（X-Ray検証用）

    目的・理由:
    - X-Rayで「DB処理が遅い」ことを可視化
    - pg_sleep(3)で3秒遅延させる
    - X-Rayサービスマップで確認

    影響範囲:
    - PostgreSQL（SELECT pg_sleep(3)）
    - X-Rayトレース

    前提条件・制約:
    - 本番環境では無効化すべき
    """
    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL pg_sleep(3)）
    with xray_recorder.capture("PostgreSQL pg_sleep(3)"):
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT pg_sleep(3)")
            xray_recorder.current_subsegment().put_metadata("delay_seconds", 3)

    # 通常のタスク一覧取得
    with xray_recorder.capture("PostgreSQL SELECT tasks"):
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20")

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "db-slow", "delay_seconds": 3}


@router.get("/slow-logic", response_model=dict)
async def slow_logic_simulation() -> dict:
    """
    ロジック遅延シミュレーション（X-Ray検証用）

    目的・理由:
    - X-Rayで「アプリケーションロジックが遅い」ことを可視化
    - time.sleep(5)で5秒遅延させる
    - X-Rayサービスマップで確認

    影響範囲:
    - アプリケーション処理（time.sleep）
    - X-Rayトレース

    前提条件・制約:
    - 本番環境では無効化すべき
    - 非同期処理をブロックするため注意
    """
    # X-Rayサブセグメント（Business Logic）
    with xray_recorder.capture("Business Logic"):
        time.sleep(5)
        xray_recorder.current_subsegment().put_metadata("delay_seconds", 5)

    # 通常のタスク一覧取得
    pool = await get_db_pool()
    with xray_recorder.capture("PostgreSQL SELECT tasks"):
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20")

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "logic-slow", "delay_seconds": 5}


@router.get("/slow-external", response_model=dict)
async def slow_external_simulation() -> dict:
    """
    外部API遅延シミュレーション（X-Ray検証用）

    目的・理由:
    - X-Rayで「外部API呼び出しが遅い」ことを可視化
    - httpbin.org/delay/2で2秒遅延させる
    - X-Rayサービスマップで確認

    影響範囲:
    - 外部API（httpbin.org）
    - X-Rayトレース

    前提条件・制約:
    - 本番環境では無効化すべき
    - httpbin.orgが利用可能であること
    """
    # X-Rayサブセグメント（External API httpbin.org）
    with xray_recorder.capture("External API httpbin.org"):
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/delay/2", timeout=10.0)
            xray_recorder.current_subsegment().put_metadata("external_api_status", response.status_code)
            xray_recorder.current_subsegment().put_metadata("delay_seconds", 2)

    # 通常のタスク一覧取得
    pool = await get_db_pool()
    with xray_recorder.capture("PostgreSQL SELECT tasks"):
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20")

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "external-slow", "delay_seconds": 2}
