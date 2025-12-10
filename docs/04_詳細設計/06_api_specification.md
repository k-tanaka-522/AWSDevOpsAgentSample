# API仕様書

## 概要

### API概要

X-Ray Watch POCのサンプルアプリケーションAPI仕様。

| 項目 | 内容 |
|------|------|
| API名 | タスク管理API + 障害シミュレーションAPI |
| ベースURL | `https://<ALB_DNS_NAME>` |
| 認証 | なし（POC簡略化） |
| データフォーマット | JSON |
| 文字コード | UTF-8 |

### APIエンドポイント一覧

| カテゴリ | メソッド | エンドポイント | 説明 |
|---------|----------|---------------|------|
| **ヘルスチェック** | GET | `/health` | ヘルスチェック |
| **タスク管理** | GET | `/tasks` | タスク一覧取得 |
| **タスク管理** | GET | `/tasks/{id}` | タスク詳細取得 |
| **タスク管理** | POST | `/tasks` | タスク作成 |
| **タスク管理** | PUT | `/tasks/{id}` | タスク更新 |
| **タスク管理** | DELETE | `/tasks/{id}` | タスク削除 |
| **障害シミュレーション** | GET | `/tasks/slow-db` | DB遅延シミュレーション |
| **障害シミュレーション** | GET | `/tasks/slow-logic` | ロジック遅延シミュレーション |
| **障害シミュレーション** | GET | `/tasks/slow-external` | 外部API遅延シミュレーション |

## データモデル

### Task

| フィールド | 型 | 説明 | 必須 | 制約 |
|-----------|-----|------|------|------|
| `id` | UUID | タスクID（自動生成） | ○ | 読み取り専用 |
| `title` | String | タスク名 | ○ | 最大100文字 |
| `description` | String | 詳細説明 | - | 最大500文字 |
| `status` | Enum | ステータス | ○ | `pending`, `in_progress`, `completed` |
| `created_at` | DateTime | 作成日時 | ○ | 読み取り専用、ISO 8601形式 |
| `updated_at` | DateTime | 更新日時 | ○ | 読み取り専用、ISO 8601形式 |

**JSON例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "X-Ray検証タスク",
  "description": "AWS X-Rayの分散トレーシング検証",
  "status": "in_progress",
  "created_at": "2025-12-10T12:00:00Z",
  "updated_at": "2025-12-10T12:30:00Z"
}
```

## APIエンドポイント詳細

### 1. ヘルスチェック

**エンドポイント**: `GET /health`

**用途**: ALBヘルスチェック、監視

**リクエスト**: なし

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 正常 | `{"status": "healthy"}` |
| 503 Service Unavailable | 異常（DB接続不可等） | `{"status": "unhealthy", "reason": "..."}` |

**レスポンス例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-10T12:00:00Z",
  "version": "1.0.0"
}
```

**X-Rayトレース**: なし（軽量エンドポイント）

---

### 2. タスク一覧取得

**エンドポイント**: `GET /tasks`

**用途**: タスク一覧を取得

**リクエストパラメータ**:

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|----------|-----|------|----------|------|
| `status` | String | - | - | ステータスフィルター（`pending`, `in_progress`, `completed`） |
| `limit` | Integer | - | 20 | 取得件数（最大100） |
| `offset` | Integer | - | 0 | オフセット |

**リクエスト例**:
```
GET /tasks?status=in_progress&limit=10&offset=0
```

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功 | タスク配列 |
| 400 Bad Request | パラメータ不正 | エラーメッセージ |

**レスポンス例**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "X-Ray検証タスク",
      "description": "AWS X-Rayの分散トレーシング検証",
      "status": "in_progress",
      "created_at": "2025-12-10T12:00:00Z",
      "updated_at": "2025-12-10T12:30:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

**X-Rayトレース**:
- セグメント: `GET /tasks`
- サブセグメント: `PostgreSQL SELECT tasks`

---

### 3. タスク詳細取得

**エンドポイント**: `GET /tasks/{id}`

**用途**: タスク詳細を取得

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|----------|-----|------|
| `id` | UUID | タスクID |

**リクエスト例**:
```
GET /tasks/550e8400-e29b-41d4-a716-446655440000
```

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功 | タスクオブジェクト |
| 404 Not Found | タスクが存在しない | エラーメッセージ |

**レスポンス例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "X-Ray検証タスク",
  "description": "AWS X-Rayの分散トレーシング検証",
  "status": "in_progress",
  "created_at": "2025-12-10T12:00:00Z",
  "updated_at": "2025-12-10T12:30:00Z"
}
```

**X-Rayトレース**:
- セグメント: `GET /tasks/{id}`
- サブセグメント: `PostgreSQL SELECT tasks WHERE id = ?`

---

### 4. タスク作成

**エンドポイント**: `POST /tasks`

**用途**: 新規タスクを作成

**リクエストボディ**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `title` | String | ○ | タスク名（最大100文字） |
| `description` | String | - | 詳細説明（最大500文字） |
| `status` | Enum | - | ステータス（デフォルト: `pending`） |

**リクエスト例**:
```json
{
  "title": "X-Ray検証タスク",
  "description": "AWS X-Rayの分散トレーシング検証",
  "status": "pending"
}
```

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 201 Created | 成功 | 作成されたタスクオブジェクト |
| 400 Bad Request | バリデーションエラー | エラーメッセージ |

**レスポンス例**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "X-Ray検証タスク",
  "description": "AWS X-Rayの分散トレーシング検証",
  "status": "pending",
  "created_at": "2025-12-10T12:00:00Z",
  "updated_at": "2025-12-10T12:00:00Z"
}
```

**X-Rayトレース**:
- セグメント: `POST /tasks`
- サブセグメント: `PostgreSQL INSERT INTO tasks`

---

### 5. タスク更新

**エンドポイント**: `PUT /tasks/{id}`

**用途**: タスクを更新

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|----------|-----|------|
| `id` | UUID | タスクID |

**リクエストボディ**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `title` | String | - | タスク名（最大100文字） |
| `description` | String | - | 詳細説明（最大500文字） |
| `status` | Enum | - | ステータス |

**リクエスト例**:
```json
{
  "status": "completed"
}
```

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功 | 更新されたタスクオブジェクト |
| 400 Bad Request | バリデーションエラー | エラーメッセージ |
| 404 Not Found | タスクが存在しない | エラーメッセージ |

**X-Rayトレース**:
- セグメント: `PUT /tasks/{id}`
- サブセグメント: `PostgreSQL UPDATE tasks WHERE id = ?`

---

### 6. タスク削除

**エンドポイント**: `DELETE /tasks/{id}`

**用途**: タスクを削除

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|----------|-----|------|
| `id` | UUID | タスクID |

**リクエスト**: なし

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 204 No Content | 成功 | なし |
| 404 Not Found | タスクが存在しない | エラーメッセージ |

**X-Rayトレース**:
- セグメント: `DELETE /tasks/{id}`
- サブセグメント: `PostgreSQL DELETE FROM tasks WHERE id = ?`

---

### 7. DB遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-db`

**用途**: X-Ray検証用（DB処理で3秒遅延）

**実装方法**: `SELECT pg_sleep(3)`

**リクエスト**: なし

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功（3秒後） | タスク配列（通常の一覧取得と同じ） |

**レスポンス例**:
```json
{
  "tasks": [...],
  "simulation": "db-slow",
  "delay_seconds": 3
}
```

**X-Rayトレース**:
- セグメント: `GET /tasks/slow-db`
- サブセグメント: `PostgreSQL pg_sleep(3)`（3秒）
- サブセグメント: `PostgreSQL SELECT tasks`

**期待される結果**: X-Rayサービスマップで「DB処理に3秒かかっている」ことが可視化される

---

### 8. ロジック遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-logic`

**用途**: X-Ray検証用（アプリ処理で5秒遅延）

**実装方法**: `time.sleep(5)`（Python）

**リクエスト**: なし

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功（5秒後） | タスク配列（通常の一覧取得と同じ） |

**レスポンス例**:
```json
{
  "tasks": [...],
  "simulation": "logic-slow",
  "delay_seconds": 5
}
```

**X-Rayトレース**:
- セグメント: `GET /tasks/slow-logic`
- サブセグメント: `Business Logic`（5秒）
- サブセグメント: `PostgreSQL SELECT tasks`

**期待される結果**: X-Rayサービスマップで「アプリケーションロジックに5秒かかっている」ことが可視化される

---

### 9. 外部API遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-external`

**用途**: X-Ray検証用（外部API呼び出しで2秒遅延）

**実装方法**: モック外部API（`httpbin.org/delay/2`）呼び出し

**リクエスト**: なし

**レスポンス**:

| ステータスコード | 説明 | ボディ |
|---------------|------|--------|
| 200 OK | 成功（2秒後） | タスク配列（通常の一覧取得と同じ） |

**レスポンス例**:
```json
{
  "tasks": [...],
  "simulation": "external-slow",
  "delay_seconds": 2
}
```

**X-Rayトレース**:
- セグメント: `GET /tasks/slow-external`
- サブセグメント: `External API httpbin.org`（2秒）
- サブセグメント: `PostgreSQL SELECT tasks`

**期待される結果**: X-Rayサービスマップで「外部API呼び出しに2秒かかっている」ことが可視化される

---

## エラーレスポンス

### エラーレスポンス形式

すべてのエラーは以下の形式で返却されます。

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "details": {
      "field": "title",
      "constraint": "required"
    }
  },
  "trace_id": "1-67890abc-def1234567890abc"
}
```

### エラーコード一覧

| HTTPステータス | エラーコード | 説明 |
|--------------|------------|------|
| 400 | `VALIDATION_ERROR` | バリデーションエラー |
| 404 | `NOT_FOUND` | リソースが存在しない |
| 500 | `INTERNAL_SERVER_ERROR` | サーバーエラー |
| 503 | `SERVICE_UNAVAILABLE` | サービス利用不可（DB接続不可等） |

## X-Rayトレーシング仕様

### トレースヘッダー

**リクエストヘッダー**: `X-Amzn-Trace-Id`（ALBが自動付与）

**例**:
```
X-Amzn-Trace-Id: Root=1-67890abc-def1234567890abc;Parent=1234567890abcdef;Sampled=1
```

### トレース構造

```
Trace (全体)
├─ Segment: ALB (ALBが自動生成)
├─ Segment: ECS (アプリケーションが生成)
│  ├─ Subsegment: Business Logic
│  ├─ Subsegment: PostgreSQL Query
│  └─ Subsegment: External API (該当する場合)
└─ Segment: X-Ray Daemon (トレース送信)
```

### カスタム属性（Annotations）

以下の属性をX-Rayに送信します。

| 属性名 | 説明 | 例 |
|--------|------|---|
| `user_id` | ユーザーID | `user123` |
| `request_id` | リクエストID | `req-456` |
| `environment` | 環境 | `production` |
| `version` | アプリバージョン | `1.0.0` |

### カスタムメタデータ（Metadata）

| メタデータ名 | 説明 | 例 |
|------------|------|---|
| `request` | リクエスト詳細 | `{"method": "GET", "path": "/tasks"}` |
| `response` | レスポンス詳細 | `{"status": 200, "size": 1024}` |
| `sql_query` | 実行SQLクエリ | `SELECT * FROM tasks WHERE id = ?` |

## データベーススキーマ

### tasks テーブル

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

## 実装方針

### 推奨フレームワーク

- **Python**: FastAPI（非同期対応、OpenAPI自動生成）
- **X-Ray SDK**: `aws-xray-sdk-python`
- **DB接続**: `asyncpg`（非同期PostgreSQL）

### ディレクトリ構成（参考）

```
src/
├── main.py                # FastAPIエントリポイント
├── api/
│   ├── tasks.py          # タスクAPIエンドポイント
│   └── health.py         # ヘルスチェック
├── models/
│   └── task.py           # Taskモデル
├── db/
│   └── postgres.py       # PostgreSQL接続
└── middleware/
    └── xray.py           # X-Rayミドルウェア
```

## 参照ドキュメント

- [要件定義書: 機能要件](../02_要件定義/要件定義書.md#3-機能要件)
- [基本設計: 08_監視・アラート設計.md](../03_基本設計/08_監視・アラート設計.md)

---

**作成者**: infra-architect (via PM)
**作成日**: 2025-12-10
**バージョン**: 1.0
