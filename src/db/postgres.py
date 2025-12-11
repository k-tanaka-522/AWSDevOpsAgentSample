"""
PostgreSQL接続管理

目的: 非同期PostgreSQL接続の初期化とコネクションプール管理
理由: asyncpgでパフォーマンス最適化、接続の再利用
影響範囲: すべてのDB操作
前提条件: DATABASE_URL環境変数が設定されていること
"""

import os
from typing import Optional

import asyncpg
from aws_xray_sdk.core import xray_recorder


class Database:
    """
    データベース接続クラス

    目的: asyncpgコネクションプールの管理
    理由: 接続の再利用でパフォーマンス向上
    影響範囲: すべてのDB操作
    前提条件: DATABASE_URL環境変数が設定されていること
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """
        DB接続を確立

        目的: コネクションプールの初期化
        理由: アプリ起動時に接続を確立
        影響範囲: アプリケーション全体のDB操作
        前提条件: DATABASE_URLが有効であること
        """
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )

    async def disconnect(self):
        """
        DB接続を切断

        目的: コネクションプールのクリーンアップ
        理由: アプリ終了時にリソースを解放
        影響範囲: アプリケーション終了処理
        前提条件: poolが初期化されていること
        """
        if self.pool:
            await self.pool.close()

    async def execute_with_xray(self, query: str, *args, operation_name: str = "PostgreSQL Query"):
        """
        X-Rayトレース付きでSQLクエリを実行（更新系）

        目的: INSERT/UPDATE/DELETE操作をX-Rayで可視化
        理由: DB操作のボトルネックを特定するため
        影響範囲: すべての更新系DB操作
        前提条件: X-Rayが有効化されていること
        """
        subsegment = xray_recorder.begin_subsegment(operation_name)
        try:
            subsegment.put_metadata("sql_query", query)
            subsegment.put_annotation("db_type", "PostgreSQL")

            async with self.pool.acquire() as connection:
                result = await connection.execute(query, *args)

            return result
        except Exception as e:
            subsegment.put_metadata("error", str(e))
            raise
        finally:
            xray_recorder.end_subsegment()

    async def fetch_with_xray(self, query: str, *args, operation_name: str = "PostgreSQL SELECT"):
        """
        X-Rayトレース付きでSQLクエリを実行（参照系、複数行）

        目的: SELECT操作（複数行）をX-Rayで可視化
        理由: DB操作のボトルネックを特定するため
        影響範囲: すべての参照系DB操作（複数行）
        前提条件: X-Rayが有効化されていること
        """
        subsegment = xray_recorder.begin_subsegment(operation_name)
        try:
            subsegment.put_metadata("sql_query", query)
            subsegment.put_annotation("db_type", "PostgreSQL")

            async with self.pool.acquire() as connection:
                rows = await connection.fetch(query, *args)

            subsegment.put_metadata("row_count", len(rows))
            return rows
        except Exception as e:
            subsegment.put_metadata("error", str(e))
            raise
        finally:
            xray_recorder.end_subsegment()

    async def fetchrow_with_xray(self, query: str, *args, operation_name: str = "PostgreSQL SELECT ONE"):
        """
        X-Rayトレース付きでSQLクエリを実行（参照系、1行）

        目的: SELECT操作（1行）をX-Rayで可視化
        理由: DB操作のボトルネックを特定するため
        影響範囲: すべての参照系DB操作（1行）
        前提条件: X-Rayが有効化されていること
        """
        subsegment = xray_recorder.begin_subsegment(operation_name)
        try:
            subsegment.put_metadata("sql_query", query)
            subsegment.put_annotation("db_type", "PostgreSQL")

            async with self.pool.acquire() as connection:
                row = await connection.fetchrow(query, *args)

            return row
        except Exception as e:
            subsegment.put_metadata("error", str(e))
            raise
        finally:
            xray_recorder.end_subsegment()


# グローバルインスタンス
db = Database()
