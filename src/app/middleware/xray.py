"""
X-Rayミドルウェア

目的・理由:
- FastAPIリクエストをX-Rayでトレーシング
- ALBから送信されるX-Amzn-Trace-Idヘッダーを読み取り、トレースを継続
- カスタム属性（Annotations/Metadata）を追加

影響範囲:
- すべてのAPIエンドポイント
- X-Rayトレース送信

前提条件・制約:
- X-Ray Daemonが稼働していること（UDP 2000番ポート）
- 環境変数ENVIRONMENT, VERSIONが設定されていること（任意）
"""

import os
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware as BaseXRayMiddleware


class XRayMiddleware(BaseHTTPMiddleware):
    """
    X-Rayトレーシングミドルウェア

    目的・理由:
    - FastAPIリクエストごとにX-Rayセグメントを作成
    - ALBから送信されるトレースIDを継承
    - カスタム属性をX-Rayに送信

    影響範囲:
    - すべてのAPIエンドポイント

    前提条件・制約:
    - X-Ray Daemonが稼働していること
    """

    def __init__(self, app):
        super().__init__(app)

        # X-Ray Recorderの設定
        xray_recorder.configure(
            service="xray-watch-poc",
            daemon_address=os.environ.get("XRAY_DAEMON_ADDRESS", "127.0.0.1:2000"),
            sampling=True,  # サンプリングを有効化
            context_missing="LOG_ERROR",  # コンテキストがない場合はログ出力
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        リクエスト処理のラップ

        目的・理由:
        - リクエストごとにX-Rayセグメントを作成
        - ALBから送信されるX-Amzn-Trace-Idヘッダーを読み取り
        - カスタム属性（Annotations/Metadata）を追加

        影響範囲:
        - すべてのAPIエンドポイント

        前提条件・制約:
        - X-Amzn-Trace-Idヘッダーが存在する場合のみトレース継続
        """
        # X-Amzn-Trace-Idヘッダーからトレース情報を取得
        trace_header = request.headers.get("X-Amzn-Trace-Id")

        # セグメント名（エンドポイント）
        segment_name = f"{request.method} {request.url.path}"

        # X-Rayセグメント開始
        segment = xray_recorder.begin_segment(
            name=segment_name,
            traceid=self._extract_trace_id(trace_header) if trace_header else None,
            parent_id=self._extract_parent_id(trace_header) if trace_header else None,
            sampling=self._extract_sampling(trace_header) if trace_header else 1,
        )

        try:
            # カスタム属性（Annotations）
            segment.put_annotation("environment", os.environ.get("ENVIRONMENT", "development"))
            segment.put_annotation("version", os.environ.get("VERSION", "1.0.0"))
            segment.put_annotation("method", request.method)
            segment.put_annotation("path", request.url.path)

            # カスタムメタデータ（Metadata）
            segment.put_metadata(
                "request",
                {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": str(request.query_params),
                    "headers": dict(request.headers),
                },
            )

            # リクエスト処理
            response = await call_next(request)

            # レスポンスメタデータ
            segment.put_metadata(
                "response",
                {
                    "status": response.status_code,
                    "headers": dict(response.headers),
                },
            )

            return response

        except Exception as e:
            # エラー情報をX-Rayに記録
            segment.put_metadata("error", {"message": str(e), "type": type(e).__name__})
            raise

        finally:
            # X-Rayセグメント終了
            xray_recorder.end_segment()

    @staticmethod
    def _extract_trace_id(trace_header: str) -> str | None:
        """
        X-Amzn-Trace-IdヘッダーからトレースIDを抽出

        目的・理由:
        - ALBから送信されるトレースIDを継承
        - 分散トレーシングを実現

        影響範囲:
        - X-Rayトレース

        前提条件・制約:
        - trace_headerが"Root=1-xxx-xxx"形式であること
        """
        if not trace_header:
            return None

        parts = trace_header.split(";")
        for part in parts:
            if part.startswith("Root="):
                return part.replace("Root=", "").strip()

        return None

    @staticmethod
    def _extract_parent_id(trace_header: str) -> str | None:
        """
        X-Amzn-Trace-IdヘッダーからParent IDを抽出

        目的・理由:
        - ALBから送信される親セグメントIDを継承

        影響範囲:
        - X-Rayトレース

        前提条件・制約:
        - trace_headerが"Parent=xxx"形式を含むこと
        """
        if not trace_header:
            return None

        parts = trace_header.split(";")
        for part in parts:
            if part.startswith("Parent="):
                return part.replace("Parent=", "").strip()

        return None

    @staticmethod
    def _extract_sampling(trace_header: str) -> int:
        """
        X-Amzn-Trace-IdヘッダーからSampledフラグを抽出

        目的・理由:
        - ALBのサンプリング判定を継承

        影響範囲:
        - X-Rayトレース

        前提条件・制約:
        - trace_headerが"Sampled=0/1"形式を含むこと
        """
        if not trace_header:
            return 1  # デフォルトはサンプリング有効

        parts = trace_header.split(";")
        for part in parts:
            if part.startswith("Sampled="):
                return int(part.replace("Sampled=", "").strip())

        return 1
