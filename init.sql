-- X-Ray Watch POC - テーブル初期化
--
-- 目的・理由:
-- - PostgreSQL初回起動時にtasksテーブルを作成
-- - インデックスを設定し、パフォーマンスを最適化
-- - サンプルデータを挿入
--
-- 影響範囲:
-- - PostgreSQLデータベース（xray_watch）
--
-- 前提条件・制約:
-- - PostgreSQL 15以上
-- - gen_random_uuid()が使用可能

-- tasksテーブル作成
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- サンプルデータ挿入
INSERT INTO tasks (title, description, status) VALUES
    ('X-Ray検証タスク1', 'AWS X-Rayの分散トレーシング検証', 'in_progress'),
    ('X-Ray検証タスク2', 'DB遅延シミュレーション検証', 'pending'),
    ('X-Ray検証タスク3', 'ロジック遅延シミュレーション検証', 'pending'),
    ('X-Ray検証タスク4', '外部API遅延シミュレーション検証', 'completed')
ON CONFLICT DO NOTHING;

-- 確認
SELECT COUNT(*) AS task_count FROM tasks;
