"""
PostgreSQL接続管理

目的・理由:
- asyncpgを使用した非同期PostgreSQL接続プールを管理
- アプリケーション起動時にプール作成、終了時にクローズ
- すべてのAPI処理で接続プールを再利用（パフォーマンス向上）

影響範囲:
- すべてのDBアクセス処理
- X-Rayトレース（サブセグメント）

前提条件・制約:
- DATABASE_URL環境変数が設定されていること
- PostgreSQLが稼働していること
"""

import os
from typing import Optional

import asyncpg


# グローバル接続プール
_pool: Optional[asyncpg.Pool] = None


async def init_db() -> None:
    """
    DB接続プール初期化

    目的・理由:
    - アプリケーション起動時にDB接続プールを作成
    - 複数のDB接続を再利用し、パフォーマンスを向上
    - 環境変数DATABASE_URLから接続情報を取得
    - tasksテーブルとインデックスを自動作成

    影響範囲:
    - すべてのDBアクセス処理

    前提条件・制約:
    - DATABASE_URL環境変数が設定されていること
    - 形式: postgresql://user:password@host:port/database
    """
    global _pool

    database_url = os.environ.get(
        "DATABASE_URL", "postgresql://xray_user:xray_password@localhost:5432/xray_watch"
    )

    _pool = await asyncpg.create_pool(
        database_url,
        min_size=2,  # 最小接続数
        max_size=10,  # 最大接続数
        command_timeout=60,  # コマンドタイムアウト（秒）
    )

    print(f"✅ Database connection pool created: {database_url}")

    # テーブルとインデックスの自動作成
    try:
        async with _pool.acquire() as conn:
            # tasksテーブル作成
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    title VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    status VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'completed')),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );
            """)

            # インデックス作成
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);")

            # サンプルデータ挿入
            await conn.execute("""
                INSERT INTO tasks (title, description, status) VALUES
                    ('X-Ray検証タスク1', 'AWS X-Rayの分散トレーシング検証', 'in_progress'),
                    ('X-Ray検証タスク2', 'DB遅延シミュレーション検証', 'pending'),
                    ('X-Ray検証タスク3', 'ロジック遅延シミュレーション検証', 'pending'),
                    ('X-Ray検証タスク4', '外部API遅延シミュレーション検証', 'completed')
                ON CONFLICT DO NOTHING;
            """)

            print("✅ Database migration completed")
    except Exception as e:
        print(f"⚠️ Database migration failed: {e}")
        # アプリケーションは起動を継続


async def close_db() -> None:
    """
    DB接続プールクローズ

    目的・理由:
    - アプリケーション終了時にDB接続プールを適切にクローズ
    - リソースリークを防ぐ

    影響範囲:
    - すべてのDBアクセス処理

    前提条件・制約:
    - init_db()が事前に実行されていること
    """
    global _pool

    if _pool:
        await _pool.close()
        print("✅ Database connection pool closed")


async def get_db_pool() -> asyncpg.Pool:
    """
    DB接続プール取得

    目的・理由:
    - 各API処理でDB接続プールを取得
    - グローバル変数_poolを返す

    影響範囲:
    - すべてのDBアクセス処理

    前提条件・制約:
    - init_db()が事前に実行されていること
    """
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")

    return _pool
