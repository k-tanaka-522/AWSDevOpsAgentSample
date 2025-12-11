"""
タスクモデル定義

目的: タスクAPIのリクエスト/レスポンスモデルを定義
理由: Pydanticによるバリデーション、型安全性、OpenAPI自動生成
影響範囲: すべてのタスクAPI
前提条件: なし
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """
    タスクステータス列挙型

    目的: ステータスの型安全性確保
    理由: 不正な値の入力を防ぐ
    影響範囲: タスク作成・更新API
    前提条件: DB側でもCHECK制約が必要
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskBase(BaseModel):
    """
    タスク基底モデル（共通フィールド）

    目的: タスクの共通フィールドを定義
    理由: 作成・更新リクエストで共有
    影響範囲: TaskCreate、TaskUpdate、TaskResponse
    前提条件: なし
    """
    title: str = Field(..., max_length=100, description="タスク名")
    description: Optional[str] = Field(None, max_length=500, description="詳細説明")
    status: TaskStatus = Field(TaskStatus.PENDING, description="ステータス")


class TaskCreate(TaskBase):
    """
    タスク作成リクエストモデル

    目的: POST /tasks のリクエストボディ
    理由: タイトルは必須、その他は任意
    影響範囲: POST /tasks
    前提条件: なし
    """
    pass


class TaskUpdate(BaseModel):
    """
    タスク更新リクエストモデル

    目的: PUT /tasks/{id} のリクエストボディ
    理由: すべてのフィールドが任意（部分更新）
    影響範囲: PUT /tasks/{id}
    前提条件: 少なくとも1つのフィールドが指定されること
    """
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    """
    タスクレスポンスモデル

    目的: タスクAPIのレスポンス
    理由: DBから取得したタスクをJSON形式で返却
    影響範囲: すべてのタスクAPI
    前提条件: DBにタスクレコードが存在すること
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """
    タスク一覧レスポンスモデル

    目的: GET /tasks のレスポンス
    理由: ページネーション情報を含める
    影響範囲: GET /tasks
    前提条件: なし
    """
    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """
    エラーレスポンスモデル

    目的: 統一されたエラーレスポンス形式
    理由: API仕様書に準拠
    影響範囲: すべてのエラーレスポンス
    前提条件: なし
    """
    error: dict
    trace_id: Optional[str] = None
