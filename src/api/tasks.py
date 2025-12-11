"""
タスクAPIエンドポイント

目的: タスク管理API + 障害シミュレーションAPI
理由: X-Ray検証用のサンプルアプリケーション
影響範囲: フロントエンド、X-Rayトレーシング
前提条件: tasksテーブルが存在すること
"""

import asyncio
import time
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from aws_xray_sdk.core import xray_recorder

from db.postgres import db
from models.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskStatus,
    ErrorResponse
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    タスク一覧取得

    目的: タスク一覧をページネーション付きで取得
    理由: タスク管理機能
    影響範囲: フロントエンド一覧画面
    前提条件: tasksテーブルが存在すること
    """
    try:
        # クエリ構築
        if status_filter:
            query = """
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            """
            count_query = "SELECT COUNT(*) FROM tasks WHERE status = $1"

            tasks = await db.fetch_with_xray(
                query, status_filter.value, limit, offset,
                operation_name="PostgreSQL SELECT tasks (filtered)"
            )
            total = await db.fetchrow_with_xray(
                count_query, status_filter.value,
                operation_name="PostgreSQL COUNT tasks (filtered)"
            )
        else:
            query = """
                SELECT id, title, description, status, created_at, updated_at
                FROM tasks
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            count_query = "SELECT COUNT(*) FROM tasks"

            tasks = await db.fetch_with_xray(
                query, limit, offset,
                operation_name="PostgreSQL SELECT tasks"
            )
            total = await db.fetchrow_with_xray(
                count_query,
                operation_name="PostgreSQL COUNT tasks"
            )

        return TaskListResponse(
            tasks=[TaskResponse(**dict(task)) for task in tasks],
            total=total[0],
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID):
    """
    タスク詳細取得

    目的: タスク詳細を取得
    理由: タスク詳細画面
    影響範囲: フロントエンド詳細画面
    前提条件: 指定されたIDのタスクが存在すること
    """
    try:
        query = """
            SELECT id, title, description, status, created_at, updated_at
            FROM tasks
            WHERE id = $1
        """

        task = await db.fetchrow_with_xray(
            query, task_id,
            operation_name=f"PostgreSQL SELECT tasks WHERE id = {task_id}"
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}}
            )

        return TaskResponse(**dict(task))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """
    タスク作成

    目的: 新規タスクを作成
    理由: タスク作成機能
    影響範囲: tasksテーブル
    前提条件: titleが必須
    """
    try:
        query = """
            INSERT INTO tasks (title, description, status)
            VALUES ($1, $2, $3)
            RETURNING id, title, description, status, created_at, updated_at
        """

        row = await db.fetchrow_with_xray(
            query, task.title, task.description, task.status.value,
            operation_name="PostgreSQL INSERT INTO tasks"
        )

        return TaskResponse(**dict(row))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, task: TaskUpdate):
    """
    タスク更新

    目的: タスクを更新
    理由: タスク編集機能
    影響範囲: tasksテーブル
    前提条件: 指定されたIDのタスクが存在すること
    """
    try:
        # 更新するフィールドを動的に構築
        fields = []
        values = []
        param_idx = 1

        if task.title is not None:
            fields.append(f"title = ${param_idx}")
            values.append(task.title)
            param_idx += 1

        if task.description is not None:
            fields.append(f"description = ${param_idx}")
            values.append(task.description)
            param_idx += 1

        if task.status is not None:
            fields.append(f"status = ${param_idx}")
            values.append(task.status.value)
            param_idx += 1

        if not fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "VALIDATION_ERROR", "message": "No fields to update"}}
            )

        # updated_atを更新
        fields.append(f"updated_at = NOW()")

        values.append(task_id)
        query = f"""
            UPDATE tasks
            SET {', '.join(fields)}
            WHERE id = ${param_idx}
            RETURNING id, title, description, status, created_at, updated_at
        """

        row = await db.fetchrow_with_xray(
            query, *values,
            operation_name=f"PostgreSQL UPDATE tasks WHERE id = {task_id}"
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}}
            )

        return TaskResponse(**dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID):
    """
    タスク削除

    目的: タスクを削除
    理由: タスク削除機能
    影響範囲: tasksテーブル
    前提条件: 指定されたIDのタスクが存在すること
    """
    try:
        query = "DELETE FROM tasks WHERE id = $1"

        result = await db.execute_with_xray(
            query, task_id,
            operation_name=f"PostgreSQL DELETE FROM tasks WHERE id = {task_id}"
        )

        # resultは "DELETE 1" のような文字列
        if result == "DELETE 0":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": f"Task {task_id} not found"}}
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


# --- 障害シミュレーションエンドポイント ---

@router.get("/slow-db", response_model=dict)
async def simulate_slow_db(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    DB遅延シミュレーション

    目的: X-Ray検証用（DB処理で3秒遅延）
    理由: DBボトルネックをX-Rayで可視化
    影響範囲: X-Rayトレース
    前提条件: PostgreSQLのpg_sleep関数が利用可能
    """
    try:
        # pg_sleep(3)で3秒遅延
        await db.execute_with_xray(
            "SELECT pg_sleep(3)",
            operation_name="PostgreSQL pg_sleep(3)"
        )

        # 通常のタスク取得
        query = """
            SELECT id, title, description, status, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        tasks = await db.fetch_with_xray(
            query, limit, offset,
            operation_name="PostgreSQL SELECT tasks"
        )

        return {
            "tasks": [TaskResponse(**dict(task)) for task in tasks],
            "simulation": "db-slow",
            "delay_seconds": 3
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.get("/slow-logic", response_model=dict)
async def simulate_slow_logic(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    ロジック遅延シミュレーション

    目的: X-Ray検証用（アプリ処理で5秒遅延）
    理由: アプリケーションロジックのボトルネックをX-Rayで可視化
    影響範囲: X-Rayトレース
    前提条件: なし
    """
    try:
        # ビジネスロジック遅延（5秒）
        subsegment = xray_recorder.begin_subsegment("Business Logic")
        try:
            subsegment.put_metadata("operation", "heavy_computation")
            # 非同期処理でsleepするため、asyncio.sleepを使用
            await asyncio.sleep(5)
        finally:
            xray_recorder.end_subsegment()

        # 通常のタスク取得
        query = """
            SELECT id, title, description, status, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        tasks = await db.fetch_with_xray(
            query, limit, offset,
            operation_name="PostgreSQL SELECT tasks"
        )

        return {
            "tasks": [TaskResponse(**dict(task)) for task in tasks],
            "simulation": "logic-slow",
            "delay_seconds": 5
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )


@router.get("/slow-external", response_model=dict)
async def simulate_slow_external(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    外部API遅延シミュレーション

    目的: X-Ray検証用（外部API呼び出しで2秒遅延）
    理由: 外部API呼び出しのボトルネックをX-Rayで可視化
    影響範囲: X-Rayトレース
    前提条件: httpbin.orgにアクセス可能
    """
    try:
        # 外部API呼び出し（2秒遅延）
        subsegment = xray_recorder.begin_subsegment("External API httpbin.org")
        try:
            subsegment.put_metadata("url", "https://httpbin.org/delay/2")
            subsegment.put_annotation("api_type", "external")

            async with httpx.AsyncClient() as client:
                response = await client.get("https://httpbin.org/delay/2", timeout=10.0)
                subsegment.put_metadata("status_code", response.status_code)
        finally:
            xray_recorder.end_subsegment()

        # 通常のタスク取得
        query = """
            SELECT id, title, description, status, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        tasks = await db.fetch_with_xray(
            query, limit, offset,
            operation_name="PostgreSQL SELECT tasks"
        )

        return {
            "tasks": [TaskResponse(**dict(task)) for task in tasks],
            "simulation": "external-slow",
            "delay_seconds": 2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": str(e)}}
        )
