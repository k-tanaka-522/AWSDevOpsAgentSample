# 引き継ぎドキュメント

## 現在の状況

### 完了済み
- [x] CloudFormation 全5スタック デプロイ完了
- [x] FastAPI アプリケーション実装完了（`src/` 配下）

### 残タスク
- [ ] Docker イメージビルド・ECR プッシュ
- [ ] ECS サービス更新
- [ ] X-Ray トレース動作確認

---

## AWS リソース情報

| リソース | 値 |
|---------|-----|
| リージョン | ap-northeast-1 |
| ALB DNS | `xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com` |
| ECR リポジトリ | `897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app` |
| RDS エンドポイント | `xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com` |
| RDS ポート | 5432 |
| DB シークレット ARN | `arn:aws:secretsmanager:ap-northeast-1:897167645238:secret:xray-poc-database/db/password-dfJNaW` |

---

## 手順1: Docker イメージビルド・ECR プッシュ

```bash
# 1. ECR ログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com

# 2. src ディレクトリに移動
cd src

# 3. Docker イメージビルド
docker build -t xray-poc-app .

# 4. タグ付け
docker tag xray-poc-app:latest 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest

# 5. ECR にプッシュ
docker push 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest
```

---

## 手順2: CloudFormation スタック更新（コンテナイメージ変更）

```bash
# Change Set 作成
aws cloudformation create-change-set \
  --stack-name xray-poc-compute \
  --change-set-name update-container-image \
  --use-previous-template \
  --parameters \
    ParameterKey=Environment,UsePreviousValue=true \
    ParameterKey=BaseStackName,UsePreviousValue=true \
    ParameterKey=SecurityStackName,UsePreviousValue=true \
    ParameterKey=DatabaseStackName,UsePreviousValue=true \
    ParameterKey=ContainerImage,ParameterValue=897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest \
  --region ap-northeast-1

# Change Set 確認
aws cloudformation describe-change-set \
  --stack-name xray-poc-compute \
  --change-set-name update-container-image \
  --region ap-northeast-1

# Change Set 実行
aws cloudformation execute-change-set \
  --stack-name xray-poc-compute \
  --change-set-name update-container-image \
  --region ap-northeast-1

# 完了待ち
aws cloudformation wait stack-update-complete \
  --stack-name xray-poc-compute \
  --region ap-northeast-1
```

---

## 手順3: 動作確認

```bash
# ヘルスチェック
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/

# タスク一覧
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks

# タスク作成
curl -X POST http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "description": "X-Ray POC test"}'

# DB遅延シミュレーション（X-Ray検証用）
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-db

# ロジック遅延シミュレーション
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-logic

# 外部API遅延シミュレーション
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-external
```

---

## 手順4: X-Ray コンソールで確認

1. AWS コンソール → X-Ray → Service Map
2. トレースデータが表示されることを確認
3. 遅延シミュレーションエンドポイントでボトルネック箇所を確認

---

## ファイル構成

```
src/
├── main.py                 # FastAPI エントリポイント
├── requirements.txt        # 依存関係
├── Dockerfile              # コンテナ定義（ポート80）
├── api/
│   ├── __init__.py
│   ├── health.py           # ヘルスチェック
│   └── tasks.py            # タスクAPI + 障害シミュレーション
├── models/
│   ├── __init__.py
│   └── task.py             # Pydantic モデル
├── db/
│   ├── __init__.py
│   └── postgres.py         # PostgreSQL 接続
└── middleware/
    ├── __init__.py
    └── xray.py             # X-Ray ミドルウェア
```

---

## 環境変数（ECS タスク定義で設定済み）

| 変数名 | 値 |
|--------|-----|
| AWS_XRAY_DAEMON_ADDRESS | localhost:2000 |
| AWS_REGION | ap-northeast-1 |
| DATABASE_URL | ※ Secrets Manager から取得（要追加設定） |

---

## 注意事項

1. **DATABASE_URL**: 現在のタスク定義には DATABASE_URL が設定されていません。初回デプロイ後、ECS タスクが RDS に接続できない場合は、03-compute.yaml を修正して DATABASE_URL 環境変数を追加してください。

2. **DB 初期化**: tasks テーブルが存在しない場合、アプリが起動時にエラーになります。RDS に接続して以下を実行してください:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);
```

---

**作成日**: 2025-12-11
**作成者**: PM (Claude Code)
