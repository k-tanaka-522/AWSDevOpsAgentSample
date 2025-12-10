# API 設計標準（RESTful API）

## 基本方針

- **RESTful 原則に従う**
- **HTTP メソッドの適切な使用**
- **ステータスコードの統一**
- **エラーハンドリングの標準化**
- **バージョニング戦略**
- **認証・認可の実装**
- **ドキュメント（OpenAPI/Swagger）の提供**

---

## RESTful 原則

### リソース指向

```
✅ Good: リソースを名詞で表現
GET    /users              # ユーザー一覧
GET    /users/123          # ユーザー詳細
POST   /users              # ユーザー作成
PUT    /users/123          # ユーザー更新
DELETE /users/123          # ユーザー削除

GET    /users/123/orders   # ユーザーの注文一覧
GET    /orders/456         # 注文詳細

❌ Bad: 動詞を使用
GET    /getAllUsers
POST   /createUser
POST   /deleteUser/123
GET    /getUserOrders/123
```

### HTTP メソッドの使い分け

| メソッド | 用途 | 冪等性 | 安全性 |
|---------|------|-------|-------|
| GET | リソースの取得 | ✅ | ✅ |
| POST | リソースの作成 | ❌ | ❌ |
| PUT | リソースの完全更新 | ✅ | ❌ |
| PATCH | リソースの部分更新 | ❌ | ❌ |
| DELETE | リソースの削除 | ✅ | ❌ |

```
✅ Good: HTTP メソッドの適切な使用
GET    /users              # ユーザー一覧取得
POST   /users              # ユーザー作成
PUT    /users/123          # ユーザー全体更新
PATCH  /users/123          # ユーザー部分更新
DELETE /users/123          # ユーザー削除

❌ Bad: POST ですべて処理
POST   /users/get
POST   /users/create
POST   /users/update
POST   /users/delete
```

---

## URL 設計

### 基本ルール

```
✅ Good: 小文字、ハイフン区切り
/api/v1/users
/api/v1/order-items
/api/v1/product-categories

❌ Bad: キャメルケース、アンダースコア
/api/v1/Users
/api/v1/orderItems
/api/v1/product_categories
```

### 階層構造

```
✅ Good: リソースの階層を表現
GET /users/123/orders              # ユーザー123の注文一覧
GET /users/123/orders/456          # ユーザー123の注文456
GET /orders/456/items              # 注文456の商品一覧
GET /categories/10/products        # カテゴリ10の商品一覧

❌ Bad: フラットな構造
GET /user-orders?user_id=123
GET /order-items?order_id=456
```

### クエリパラメータ

```
✅ Good: フィルタ・ソート・ページング
GET /users?status=active&sort=created_at&order=desc&page=1&limit=20

パラメータ:
- status: フィルタ条件
- sort: ソート項目
- order: asc（昇順）/ desc（降順）
- page: ページ番号
- limit: 1ページあたりの件数

❌ Bad: 複雑なクエリをパラメータで表現
GET /users?query=status:active,created_at>2024-01-01
```

---

## レスポンス形式

### 成功レスポンス

```json
// ✅ Good: 単一リソース
GET /users/123
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}

// ✅ Good: リソース一覧（ページネーション付き）
GET /users?page=1&limit=20
{
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}

// ✅ Good: 作成成功
POST /users
{
  "id": 124,
  "name": "New User",
  "email": "newuser@example.com",
  "created_at": "2024-01-15T10:00:00Z"
}

// ✅ Good: 更新成功
PUT /users/123
{
  "id": 123,
  "name": "Updated Name",
  "email": "updated@example.com",
  "updated_at": "2024-01-15T10:30:00Z"
}

// ✅ Good: 削除成功（204 No Content）
DELETE /users/123
（レスポンスボディなし）
```

### エラーレスポンス

```json
// ✅ Good: 統一されたエラー形式
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      },
      {
        "field": "password",
        "message": "Password must be at least 8 characters"
      }
    ],
    "timestamp": "2024-01-15T10:00:00Z",
    "path": "/api/v1/users"
  }
}

// ✅ Good: 認証エラー
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}

// ✅ Good: リソースが見つからない
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 123 not found",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}

// ❌ Bad: 統一されていないエラー形式
{
  "error": "Something went wrong"
}
```

---

## ステータスコード

### 成功（2xx）

| コード | 意味 | 用途 |
|-------|-----|------|
| 200 OK | 成功 | GET、PUT、PATCH の成功 |
| 201 Created | 作成成功 | POST でリソース作成 |
| 204 No Content | 成功（レスポンスなし） | DELETE の成功 |

```http
GET /users/123
200 OK

POST /users
201 Created
Location: /users/124

DELETE /users/123
204 No Content
```

### クライアントエラー（4xx）

| コード | 意味 | 用途 |
|-------|-----|------|
| 400 Bad Request | リクエストが不正 | バリデーションエラー |
| 401 Unauthorized | 認証が必要 | トークンがない、無効 |
| 403 Forbidden | 権限がない | 認証済みだが権限不足 |
| 404 Not Found | リソースが存在しない | 存在しない ID |
| 409 Conflict | 競合 | 重複データ |
| 422 Unprocessable Entity | 処理できない | バリデーションエラー（詳細） |
| 429 Too Many Requests | レート制限超過 | API 呼び出し制限 |

```http
POST /users
400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required"
  }
}

GET /users/999
404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 999 not found"
  }
}

POST /users
409 Conflict
{
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "User with this email already exists"
  }
}
```

### サーバーエラー（5xx）

| コード | 意味 | 用途 |
|-------|-----|------|
| 500 Internal Server Error | サーバーエラー | 予期しないエラー |
| 503 Service Unavailable | サービス利用不可 | メンテナンス中 |

```http
GET /users
500 Internal Server Error
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

---

## ページネーション

### オフセットベース

```
✅ Good: page & limit パラメータ
GET /users?page=1&limit=20

レスポンス:
{
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}

❌ Bad: offset が大きい場合はパフォーマンス劣化
GET /users?page=5000&limit=20
```

### カーソルベース（推奨：大規模データ）

```
✅ Good: カーソルベースのページネーション
GET /users?limit=20&cursor=eyJpZCI6MTIzfQ==

レスポンス:
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTQzfQ==",
    "has_next": true,
    "limit": 20
  }
}

次のページ:
GET /users?limit=20&cursor=eyJpZCI6MTQzfQ==
```

---

## フィルタ・ソート

### フィルタ

```
✅ Good: クエリパラメータでフィルタ
GET /users?status=active&role=admin&created_after=2024-01-01

パラメータ:
- status: ステータスでフィルタ
- role: ロールでフィルタ
- created_after: 作成日時でフィルタ
```

### ソート

```
✅ Good: sort & order パラメータ
GET /users?sort=created_at&order=desc

パラメータ:
- sort: ソート項目
- order: asc（昇順）/ desc（降順）

複数ソート:
GET /users?sort=status,created_at&order=asc,desc
```

---

## バージョニング

### URL パスでバージョン管理（推奨）

```
✅ Good: URL にバージョンを含める
/api/v1/users
/api/v2/users

メリット:
- 明確でわかりやすい
- ブラウザでアクセス可能
- キャッシュが効きやすい
```

### ヘッダーでバージョン管理

```
✅ Good: Accept ヘッダーでバージョン指定
GET /api/users
Accept: application/vnd.myapp.v1+json

GET /api/users
Accept: application/vnd.myapp.v2+json

メリット:
- URL が変わらない
- RESTful 的に正しい

デメリット:
- ブラウザでアクセスしにくい
```

---

## 認証・認可

### JWT Bearer Token（推奨）

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

レスポンス:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}

認証が必要な API 呼び出し:
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### API キー

```http
GET /api/v1/users
X-API-Key: your-api-key-here

または

GET /api/v1/users?api_key=your-api-key-here
```

### OAuth 2.0

```http
GET /api/v1/users
Authorization: Bearer oauth2-access-token

リフレッシュトークン:
POST /api/v1/auth/refresh
{
  "refresh_token": "refresh-token-here"
}

レスポンス:
{
  "access_token": "new-access-token",
  "expires_in": 3600
}
```

---

## レート制限

### ヘッダーでレート制限情報を返す

```http
GET /api/v1/users
Authorization: Bearer token

レスポンスヘッダー:
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400

レート制限超過:
429 Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit",
    "retry_after": 60
  }
}
```

---

## CORS 設定

### 適切な CORS ヘッダー

```http
レスポンスヘッダー:
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400

プリフライトリクエスト（OPTIONS）:
OPTIONS /api/v1/users
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type

レスポンス:
200 OK
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## キャッシュ制御

### Cache-Control ヘッダー

```http
✅ Good: 静的データ（ユーザープロフィール）
GET /api/v1/users/123
Cache-Control: public, max-age=3600

✅ Good: 動的データ（注文一覧）
GET /api/v1/orders
Cache-Control: no-cache

✅ Good: 機密データ
GET /api/v1/users/me
Cache-Control: private, no-store
```

### ETag

```http
GET /api/v1/users/123
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"

次回リクエスト（条件付き GET）:
GET /api/v1/users/123
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"

レスポンス（変更なし）:
304 Not Modified
```

---

## べき等性

### GET、PUT、DELETE はべき等

```
✅ Good: べき等な操作
GET    /users/123          # 何度実行しても同じ結果
PUT    /users/123          # 何度実行しても同じ結果
DELETE /users/123          # 何度実行しても同じ結果（削除済み）

❌ Bad: べき等でない操作
POST   /users              # 実行するたびに新しいユーザーが作成される
POST   /orders/123/pay     # 実行するたびに決済される（危険）
```

### POST のべき等性を担保（Idempotency Key）

```http
POST /api/v1/orders
Idempotency-Key: unique-key-12345
{
  "product_id": 1,
  "quantity": 2
}

同じ Idempotency-Key で再送:
POST /api/v1/orders
Idempotency-Key: unique-key-12345

レスポンス（同じ結果）:
200 OK（または 201 Created）
{
  "id": 789,
  "product_id": 1,
  "quantity": 2
}
```

---

## 非同期処理

### ロングランニングタスク

```http
POST /api/v1/reports/generate
{
  "report_type": "monthly_sales",
  "month": "2024-01"
}

レスポンス:
202 Accepted
Location: /api/v1/reports/jobs/abc123
{
  "job_id": "abc123",
  "status": "processing",
  "created_at": "2024-01-15T10:00:00Z"
}

ステータス確認:
GET /api/v1/reports/jobs/abc123

レスポンス:
200 OK
{
  "job_id": "abc123",
  "status": "completed",
  "result_url": "/api/v1/reports/files/report-2024-01.pdf",
  "completed_at": "2024-01-15T10:05:00Z"
}
```

---

## API ドキュメント（OpenAPI/Swagger）

### OpenAPI 3.0 仕様

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: API for user management

servers:
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users:
    get:
      summary: Get all users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

    post:
      summary: Create a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Validation error

  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
        created_at:
          type: string
          format: date-time

    CreateUserRequest:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
          maxLength: 100
        email:
          type: string
          format: email
        password:
          type: string
          minLength: 8

    Pagination:
      type: object
      properties:
        current_page:
          type: integer
        per_page:
          type: integer
        total:
          type: integer
        total_pages:
          type: integer

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

---

## ベストプラクティス

1. **RESTful 原則に従う**: リソース指向、HTTP メソッドの適切な使用
2. **ステータスコードを正しく使う**: 2xx（成功）、4xx（クライアントエラー）、5xx（サーバーエラー）
3. **エラーレスポンスを統一**: code、message、details を含める
4. **ページネーションを実装**: オフセットベース or カーソルベース
5. **バージョニング**: URL パス or ヘッダー
6. **認証・認可**: JWT Bearer Token 推奨
7. **レート制限**: API 呼び出し制限を設定
8. **CORS を適切に設定**: フロントエンドからのアクセスを許可
9. **キャッシュを活用**: Cache-Control、ETag
10. **べき等性を保証**: GET、PUT、DELETE、Idempotency Key
11. **非同期処理**: 202 Accepted でジョブ ID を返す
12. **OpenAPI ドキュメント**: API 仕様を公開

---

**参照**: `.claude/docs/10_facilitation/2.3_設計フェーズ/2.3.4_API設計/`
