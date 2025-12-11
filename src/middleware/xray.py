"""
X-Rayミドルウェア

目的: FastAPIにX-Rayトレーシングを統合
理由: すべてのHTTPリクエストをX-Rayで可視化
影響範囲: すべてのAPIエンドポイント
前提条件: AWS_XRAY_DAEMON_ADDRESSが設定されていること
"""

import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def configure_xray():
    """
    X-Rayの設定

    目的: X-Ray Daemonへの接続設定
    理由: トレースデータをX-Ray Daemonに送信するため
    影響範囲: アプリケーション全体のトレーシング
    前提条件: X-Ray Daemonが起動していること
    """
    xray_recorder.configure(
        service="x-ray-watch-api",
        daemon_address=os.getenv("AWS_XRAY_DAEMON_ADDRESS", "localhost:2000"),
        context_missing="LOG_ERROR"
    )


class XRayFastAPIMiddleware(BaseHTTPMiddleware):
    """
    FastAPI用X-Rayミドルウェア

    目的: すべてのHTTPリクエストをX-Rayセグメントでラップ
    理由: リクエスト単位でトレーシングを開始・終了
    影響範囲: すべてのAPIエンドポイント
    前提条件: configure_xray()が実行されていること
    """

    async def dispatch(self, request: Request, call_next):
        """
        リクエストごとにX-Rayセグメントを作成

        目的: HTTPリクエストをトレース
        理由: パフォーマンスボトルネックを特定
        影響範囲: すべてのHTTPリクエスト
        前提条件: X-Rayが有効化されていること
        """
        # X-Amzn-Trace-IdヘッダーからトレースIDを取得（ALBが付与）
        trace_header = request.headers.get("X-Amzn-Trace-Id")

        segment_name = f"{request.method} {request.url.path}"
        segment = xray_recorder.begin_segment(segment_name, traceid=self._parse_trace_id(trace_header))

        try:
            # リクエスト情報をアノテーション/メタデータに追加
            segment.put_annotation("http_method", request.method)
            segment.put_annotation("http_url", str(request.url))
            segment.put_metadata("request", {
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params)
            })

            # 次のミドルウェア/エンドポイントを実行
            response = await call_next(request)

            # レスポンス情報を記録
            segment.put_annotation("http_status", response.status_code)
            segment.put_metadata("response", {
                "status": response.status_code
            })

            return response
        except Exception as e:
            segment.put_metadata("error", str(e))
            raise
        finally:
            xray_recorder.end_segment()

    def _parse_trace_id(self, trace_header: str) -> str:
        """
        X-Amzn-Trace-IdヘッダーからトレースIDを抽出

        目的: ALBから渡されたトレースIDを解析
        理由: ALBのトレースと連携するため
        影響範囲: X-Rayトレース連携
        前提条件: trace_headerが有効な形式であること
        """
        if not trace_header:
            return None

        # 形式: Root=1-67890abc-def1234567890abc;Parent=1234567890abcdef;Sampled=1
        parts = trace_header.split(";")
        for part in parts:
            if part.startswith("Root="):
                return part.split("=")[1]

        return None
