"""
ヘルスチェックエンドポイント

目的: ALBヘルスチェック、監視
理由: アプリケーションの正常性を確認
影響範囲: ALBターゲットグループ、監視システム
前提条件: なし
"""

from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from db.postgres import db

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    ヘルスチェック

    目的: アプリケーションとDBの正常性を確認
    理由: ALBヘルスチェック、監視
    影響範囲: ALBターゲットグループ
    前提条件: DBが起動していること
    """
    try:
        # DB接続確認（軽量なクエリ）
        await db.pool.fetchval("SELECT 1")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )
