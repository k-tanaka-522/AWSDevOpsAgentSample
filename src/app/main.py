"""
FastAPIエントリポイント

目的・理由:
- X-Ray Watch POCのタスク管理APIを提供する
- AWS X-Rayトレーシングを統合し、分散トレーシングを実現する
- 障害シミュレーションAPIを提供し、X-Rayの可視化を検証する

影響範囲:
- すべてのAPIエンドポイント（/health, /tasks, /tasks/slow-*）
- X-Rayトレース送信（X-Ray Daemon経由）

前提条件・制約:
- PostgreSQLが稼働していること
- X-Ray Daemonが稼働していること（ECS環境）
- 環境変数が設定されていること（DATABASE_URL等）
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import health, tasks
from db.postgres import init_db, close_db
from middleware.xray import XRayMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    アプリケーションのライフサイクル管理

    目的・理由:
    - アプリ起動時にDB接続プールを初期化
    - アプリ終了時にDB接続を適切にクローズ

    影響範囲:
    - PostgreSQL接続プール（asyncpg）

    前提条件・制約:
    - DATABASE_URL環境変数が設定されていること
    """
    # 起動時処理
    await init_db()
    yield
    # 終了時処理
    await close_db()


# FastAPIアプリケーション初期化
app = FastAPI(
    title="X-Ray Watch POC API",
    description="タスク管理API + 障害シミュレーションAPI（AWS X-Rayトレーシング対応）",
    version="1.0.0",
    lifespan=lifespan,
)

# CORSミドルウェア（POC用、本番では制限すべき）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# X-Rayミドルウェア（AWS X-Rayトレーシング）
app.add_middleware(XRayMiddleware)

# ルーター登録
app.include_router(health.router)
app.include_router(tasks.router)


@app.get("/")
async def root() -> dict[str, str]:
    """
    ルートエンドポイント

    目的・理由:
    - APIの稼働確認
    - 基本情報の提供

    影響範囲:
    - なし（読み取り専用）

    前提条件・制約:
    - なし
    """
    return {
        "message": "X-Ray Watch POC API",
        "version": "1.0.0",
        "docs": "/docs",
    }
