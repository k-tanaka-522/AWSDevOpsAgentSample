"""
ヘルスチェックAPI

目的・理由:
- ALBヘルスチェック用エンドポイントを提供
- アプリケーションとDBの稼働状態を確認
- X-Rayトレースは行わない（軽量化）

影響範囲:
- ALBヘルスチェック（/health）
- 監視システム（CloudWatch等）

前提条件・制約:
- PostgreSQL接続が必要（DB接続チェックのため）
"""

from datetime import datetime

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from db.postgres import get_db_pool


router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    ヘルスチェックエンドポイント

    目的・理由:
    - ALBからのヘルスチェックに応答
    - DB接続状態を確認し、異常時は503を返す
    - X-Rayトレースは行わない（軽量エンドポイント）

    影響範囲:
    - ALBターゲットヘルス判定
    - Auto Scaling判定

    前提条件・制約:
    - PostgreSQLが稼働していること
    """
    try:
        # DB接続チェック
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")

        # 正常レスポンス
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0.0",
            },
        )

    except Exception as e:
        # DB接続不可の場合は503
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "reason": f"Database connection failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
        )
