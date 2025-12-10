# X-Ray Watch POC

AWS X-Rayを使用した分散トレーシングのPOC（Proof of Concept）プロジェクト。

## 概要

タスク管理APIを通じて、AWS X-Rayの分散トレーシング機能を検証します。

### 主要機能

- タスクCRUD操作（作成、取得、更新、削除）
- 障害シミュレーションAPI（DB遅延、ロジック遅延、外部API遅延）
- X-Rayトレーシング統合（ALB → ECS → PostgreSQL）

## アーキテクチャ

```
ALB → ECS (FastAPI + X-Ray Daemon) → RDS (PostgreSQL)
                ↓
          AWS X-Ray Console
```

## ローカル開発環境

### 前提条件

- Docker/Docker Compose
- AWS認証情報（X-Rayトレース送信用）

### 起動手順

1. **環境変数設定**

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=ap-northeast-1
```

2. **Docker Compose起動**

```bash
docker-compose up -d
```

3. **ヘルスチェック確認**

```bash
curl http://localhost:8000/health
```

4. **OpenAPI（Swagger UI）**

ブラウザで http://localhost:8000/docs にアクセス

### サービス情報

| サービス | ポート | 説明 |
|---------|-------|------|
| FastAPI | 8000 | タスク管理API |
| PostgreSQL | 5432 | データベース |
| X-Ray Daemon | 2000/udp | トレース送信 |

## APIエンドポイント

### ヘルスチェック

```bash
GET /health
```

### タスク管理

```bash
# タスク一覧取得
GET /tasks?status=in_progress&limit=10&offset=0

# タスク詳細取得
GET /tasks/{id}

# タスク作成
POST /tasks
Content-Type: application/json

{
  "title": "X-Ray検証タスク",
  "description": "AWS X-Rayの分散トレーシング検証",
  "status": "pending"
}

# タスク更新
PUT /tasks/{id}
Content-Type: application/json

{
  "status": "completed"
}

# タスク削除
DELETE /tasks/{id}
```

### 障害シミュレーション（X-Ray検証用）

```bash
# DB遅延シミュレーション（3秒）
GET /tasks/slow-db

# ロジック遅延シミュレーション（5秒）
GET /tasks/slow-logic

# 外部API遅延シミュレーション（2秒）
GET /tasks/slow-external
```

## X-Ray確認手順

1. **障害シミュレーションAPI実行**

```bash
curl http://localhost:8000/tasks/slow-db
curl http://localhost:8000/tasks/slow-logic
curl http://localhost:8000/tasks/slow-external
```

2. **AWS X-Rayコンソール確認**

- サービスマップで各コンポーネントの関係を確認
- トレースで各処理の実行時間を確認
- セグメントで詳細な処理内容を確認

## トラブルシューティング

### X-Rayトレースが送信されない

- AWS認証情報が設定されているか確認
- X-Ray Daemonが起動しているか確認
- セキュリティグループでUDP 2000番ポートが開いているか確認（ECS環境）

### PostgreSQL接続エラー

- PostgreSQLが起動しているか確認
- DATABASE_URL環境変数が正しいか確認

## 参照ドキュメント

- [API仕様書](docs/04_詳細設計/06_api_specification.md)
- [基本設計: 監視・アラート設計](docs/03_基本設計/08_監視・アラート設計.md)

## ライセンス

POCプロジェクトのため、ライセンスは設定していません。
