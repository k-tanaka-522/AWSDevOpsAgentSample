"""
FastAPIエントリポイント

目的: X-Ray Watch POC用のFastAPIアプリケーション
理由: タスク管理API + 障害シミュレーションAPI
影響範囲: アプリケーション全体
前提条件: DATABASE_URL、AWS_XRAY_DAEMON_ADDRESS環境変数が設定されていること
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api import health, tasks
from db.postgres import db
from middleware.xray import configure_xray, XRayFastAPIMiddleware

# 環境変数読み込み
load_dotenv()

# X-Ray設定
configure_xray()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理

    目的: 起動時にDB接続、終了時に切断
    理由: コネクションプールの適切な管理
    影響範囲: アプリケーション全体
    前提条件: DATABASE_URL環境変数が設定されていること
    """
    # 起動時処理
    await db.connect()
    yield
    # 終了時処理
    await db.disconnect()


# FastAPIアプリケーション初期化
app = FastAPI(
    title="X-Ray Watch API",
    description="タスク管理API + 障害シミュレーションAPI",
    version="1.0.0",
    lifespan=lifespan
)

# CORSミドルウェア（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# X-Rayミドルウェア
app.add_middleware(XRayFastAPIMiddleware)

# ルート登録
app.include_router(health.router)
app.include_router(tasks.router)


@app.get("/")
async def root():
    """
    ルートエンドポイント（ヘルスチェック用）

    目的: ALBヘルスチェック
    理由: ALBのHealthCheckPathが "/" を想定
    影響範囲: ALBターゲットグループ
    前提条件: なし
    """
    return {
        "status": "healthy",
        "message": "X-Ray Watch API is running"
    }
