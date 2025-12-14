# 障害シミュレーション機能 詳細設計書

## 概要

### 目的

AWS X-Ray検証のため、意図的に遅延・障害を発生させるAPIエンドポイントを提供し、X-Rayサービスマップ上でボトルネックを可視化する。

### スコープ

| 項目 | 内容 |
|------|------|
| 対象ファイル | `src/app/api/tasks.py` |
| 実装方法 | FastAPI エンドポイント追加 |
| X-Ray統合 | X-Ray SDK（`aws-xray-sdk-python`）でサブセグメント作成 |
| 環境制御 | 環境変数 `ENABLE_FAULT_SIMULATION` で有効/無効を制御 |

### 背景

**現在の問題**:
- 障害シミュレーションエンドポイント（`/tasks/slow-db`, `/tasks/slow-logic`, `/tasks/slow-external`）がFastAPIのルーティング順序の問題により、意図通り動作しない
- 具体的には、`GET /tasks/{task_id}` が `GET /tasks/slow-db` より先にマッチしてしまい、"slow-db" をタスクIDとして解釈されてしまう

**解決方針**:
1. ルーティング順序を修正（具体的なパス → パラメータ付きパス）
2. 環境変数による有効/無効制御を追加（本番環境保護）
3. X-Rayトレーシングを強化（遅延原因を明確に可視化）

## ファイル構成

### 修正対象ファイル

```
src/app/api/tasks.py
```

**変更内容**:
- ルーティング順序の修正
- 環境変数チェックの追加
- X-Rayサブセグメントの強化

**変更前後の比較**:

| 変更前 | 変更後 |
|-------|-------|
| エンドポイント順序が誤り | 具体的なパス → パラメータ付きパス |
| 環境制御なし | `ENABLE_FAULT_SIMULATION` で制御 |
| X-Rayサブセグメントが不完全 | すべての遅延処理にサブセグメント追加 |

## API詳細設計

### 1. ルーティング順序の修正

**問題**:
```python
# 現在の誤った順序
@router.get("", ...)                    # GET /tasks
@router.get("/{task_id}", ...)          # GET /tasks/{task_id} ← 先にマッチ
@router.post("", ...)                   # POST /tasks
@router.put("/{task_id}", ...)          # PUT /tasks/{task_id}
@router.delete("/{task_id}", ...)       # DELETE /tasks/{task_id}
@router.get("/slow-db", ...)            # GET /tasks/slow-db ← マッチしない
@router.get("/slow-logic", ...)         # GET /tasks/slow-logic ← マッチしない
@router.get("/slow-external", ...)      # GET /tasks/slow-external ← マッチしない
```

**解決**:
```python
# 修正後の正しい順序
@router.get("/slow-db", ...)            # GET /tasks/slow-db ← 具体的なパス（先）
@router.get("/slow-logic", ...)         # GET /tasks/slow-logic ← 具体的なパス（先）
@router.get("/slow-external", ...)      # GET /tasks/slow-external ← 具体的なパス（先）
@router.get("", ...)                    # GET /tasks
@router.get("/{task_id}", ...)          # GET /tasks/{task_id} ← パラメータ付き（後）
@router.post("", ...)                   # POST /tasks
@router.put("/{task_id}", ...)          # PUT /tasks/{task_id}
@router.delete("/{task_id}", ...)       # DELETE /tasks/{task_id}
```

**理由**:
- FastAPIのルーティングは、**定義順に上から評価**される
- 具体的なパス（`/slow-db`）よりも、パラメータ付きパス（`/{task_id}`）が先に定義されると、すべてのパスが `/{task_id}` にマッチしてしまう
- 具体的なパスを先に定義することで、正しくルーティングされる

### 2. 環境変数による制御

**環境変数**:
```python
ENABLE_FAULT_SIMULATION = os.getenv("ENABLE_FAULT_SIMULATION", "false").lower() == "true"
```

**環境別設定**:

| 環境 | 値 | 理由 |
|------|---|------|
| 開発（ローカル） | `true` | X-Ray検証のため有効化 |
| 本番（AWS ECS） | `false` | 意図しない遅延を防ぐため無効化 |

**エンドポイント制御**:
```python
@router.get("/slow-db", response_model=dict)
async def slow_db_simulation() -> dict:
    if not ENABLE_FAULT_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Fault simulation is disabled"}},
        )
    # ... 障害シミュレーション処理
```

**レスポンス例（無効時）**:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Fault simulation is disabled"
  }
}
```

### 3. エンドポイント詳細

#### 3.1. DB遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-db`

**目的**: PostgreSQLクエリで3秒遅延させ、X-RayでDB処理が遅いことを可視化

**実装方法**:
```python
@router.get("/slow-db", response_model=dict)
async def slow_db_simulation() -> dict:
    """
    DB遅延シミュレーション（X-Ray検証用）
    """
    # 環境変数チェック
    if not ENABLE_FAULT_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Fault simulation is disabled"}},
        )

    pool = await get_db_pool()

    # X-Rayサブセグメント（PostgreSQL pg_sleep(3)）
    with xray_recorder.capture("PostgreSQL Delay Simulation") as subsegment:
        subsegment.namespace = "remote"
        subsegment.put_annotation("simulation_type", "db-slow")
        subsegment.put_metadata("delay_seconds", 3)

        async with pool.acquire() as conn:
            query = "SELECT pg_sleep(3)"
            await conn.fetchval(query)
            subsegment.sql = {
                "database_type": "PostgreSQL",
                "url": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
                "sanitized_query": query
            }

    # 通常のタスク一覧取得
    with xray_recorder.capture("PostgreSQL SELECT tasks") as subsegment:
        subsegment.namespace = "remote"
        async with pool.acquire() as conn:
            query = "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20"
            rows = await conn.fetch(query)
            subsegment.sql = {
                "database_type": "PostgreSQL",
                "url": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
                "sanitized_query": query
            }

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "db-slow", "delay_seconds": 3}
```

**X-Rayトレース構造**:
```
Trace
└─ Segment: GET /tasks/slow-db
   ├─ Subsegment: PostgreSQL Delay Simulation (3秒)
   │  ├─ Annotation: simulation_type=db-slow
   │  └─ Metadata: delay_seconds=3
   └─ Subsegment: PostgreSQL SELECT tasks (通常処理)
```

**期待される結果**:
- X-Rayサービスマップで「PostgreSQL Delay Simulation」サブセグメントが3秒と表示される
- DBボトルネックが明確に可視化される

---

#### 3.2. ロジック遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-logic`

**目的**: アプリケーションロジックで5秒遅延させ、X-Rayでアプリ処理が遅いことを可視化

**実装方法**:
```python
@router.get("/slow-logic", response_model=dict)
async def slow_logic_simulation() -> dict:
    """
    ロジック遅延シミュレーション（X-Ray検証用）
    """
    # 環境変数チェック
    if not ENABLE_FAULT_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Fault simulation is disabled"}},
        )

    # X-Rayサブセグメント（Business Logic Delay）
    with xray_recorder.capture("Business Logic Delay Simulation") as subsegment:
        subsegment.put_annotation("simulation_type", "logic-slow")
        subsegment.put_metadata("delay_seconds", 5)
        time.sleep(5)  # 5秒遅延

    # 通常のタスク一覧取得
    pool = await get_db_pool()
    with xray_recorder.capture("PostgreSQL SELECT tasks") as subsegment:
        subsegment.namespace = "remote"
        async with pool.acquire() as conn:
            query = "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20"
            rows = await conn.fetch(query)
            subsegment.sql = {
                "database_type": "PostgreSQL",
                "url": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
                "sanitized_query": query
            }

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "logic-slow", "delay_seconds": 5}
```

**X-Rayトレース構造**:
```
Trace
└─ Segment: GET /tasks/slow-logic
   ├─ Subsegment: Business Logic Delay Simulation (5秒)
   │  ├─ Annotation: simulation_type=logic-slow
   │  └─ Metadata: delay_seconds=5
   └─ Subsegment: PostgreSQL SELECT tasks (通常処理)
```

**期待される結果**:
- X-Rayサービスマップで「Business Logic Delay Simulation」サブセグメントが5秒と表示される
- アプリケーションロジックのボトルネックが明確に可視化される

**注意**:
- `time.sleep(5)` は非同期処理をブロックするため、本番環境では絶対に使用しない（環境変数で制御）

---

#### 3.3. 外部API遅延シミュレーション

**エンドポイント**: `GET /tasks/slow-external`

**目的**: 外部API呼び出しで2秒遅延させ、X-Rayで外部API呼び出しが遅いことを可視化

**実装方法**:
```python
@router.get("/slow-external", response_model=dict)
async def slow_external_simulation() -> dict:
    """
    外部API遅延シミュレーション（X-Ray検証用）
    """
    # 環境変数チェック
    if not ENABLE_FAULT_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Fault simulation is disabled"}},
        )

    # X-Rayサブセグメント（External API httpbin.org）
    with xray_recorder.capture("External API httpbin.org Delay Simulation") as subsegment:
        subsegment.namespace = "remote"
        subsegment.put_annotation("simulation_type", "external-slow")
        subsegment.put_metadata("delay_seconds", 2)
        subsegment.put_metadata("external_url", "https://httpbin.org/delay/2")

        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/delay/2", timeout=10.0)
            subsegment.put_metadata("external_api_status", response.status_code)
            subsegment.put_metadata("external_api_response_time_ms", response.elapsed.total_seconds() * 1000)

    # 通常のタスク一覧取得
    pool = await get_db_pool()
    with xray_recorder.capture("PostgreSQL SELECT tasks") as subsegment:
        subsegment.namespace = "remote"
        async with pool.acquire() as conn:
            query = "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 20"
            rows = await conn.fetch(query)
            subsegment.sql = {
                "database_type": "PostgreSQL",
                "url": "xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com",
                "sanitized_query": query
            }

    tasks = [
        {
            "id": str(row["id"]),
            "title": row["title"],
            "description": row["description"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() + "Z",
            "updated_at": row["updated_at"].isoformat() + "Z",
        }
        for row in rows
    ]

    return {"tasks": tasks, "simulation": "external-slow", "delay_seconds": 2}
```

**X-Rayトレース構造**:
```
Trace
└─ Segment: GET /tasks/slow-external
   ├─ Subsegment: External API httpbin.org Delay Simulation (2秒)
   │  ├─ Annotation: simulation_type=external-slow
   │  ├─ Metadata: delay_seconds=2
   │  ├─ Metadata: external_url=https://httpbin.org/delay/2
   │  ├─ Metadata: external_api_status=200
   │  └─ Metadata: external_api_response_time_ms=2000
   └─ Subsegment: PostgreSQL SELECT tasks (通常処理)
```

**期待される結果**:
- X-Rayサービスマップで「External API httpbin.org Delay Simulation」サブセグメントが2秒と表示される
- 外部API依存関係が明確に可視化される

**注意**:
- `httpbin.org` が利用不可の場合、タイムアウトエラーが発生する可能性がある（timeout=10.0で制御）

---

## レスポンスモデル（Pydantic）

### 既存モデル（変更なし）

```python
class TaskResponse(BaseModel):
    """タスクレスポンス"""
    id: str
    title: str
    description: Optional[str]
    status: str
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """タスク一覧レスポンス"""
    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int
```

### 障害シミュレーション専用レスポンス

**型**: `dict`（Pydanticモデル化不要、POC簡略化）

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
  "simulation": "db-slow",
  "delay_seconds": 3
}
```

**フィールド**:

| フィールド | 型 | 説明 | 必須 |
|-----------|-----|------|------|
| `tasks` | `list[TaskResponse]` | タスク一覧（通常のタスク一覧取得と同じ） | ○ |
| `simulation` | `string` | シミュレーション種別（`db-slow`, `logic-slow`, `external-slow`） | ○ |
| `delay_seconds` | `integer` | 遅延時間（秒） | ○ |

---

## X-Ray統合設計

### 1. X-Rayサブセグメント設計

**目的**: 遅延処理を明確にX-Rayトレースに記録し、ボトルネックを可視化する

**サブセグメント命名規則**:

| シミュレーション種別 | サブセグメント名 | namespace |
|-------------------|----------------|-----------|
| DB遅延 | `PostgreSQL Delay Simulation` | `remote` |
| ロジック遅延 | `Business Logic Delay Simulation` | - |
| 外部API遅延 | `External API httpbin.org Delay Simulation` | `remote` |

**Annotation（フィルタリング用）**:

| Annotation Key | 値 | 用途 |
|---------------|---|------|
| `simulation_type` | `db-slow`, `logic-slow`, `external-slow` | X-Rayコンソールでフィルタリング |

**Metadata（詳細情報）**:

| Metadata Key | 値 | 用途 |
|-------------|---|------|
| `delay_seconds` | 遅延時間（整数） | トレース詳細で確認 |
| `external_url` | 外部APIのURL | 外部API呼び出し先の記録 |
| `external_api_status` | HTTPステータスコード | 外部APIのレスポンス状態 |
| `external_api_response_time_ms` | レスポンスタイム（ミリ秒） | 外部APIの実測値 |

### 2. X-Rayトレース例（DB遅延）

```
Trace ID: 1-67890abc-def1234567890abc
Duration: 3.12s

Segments:
├─ ALB (10ms)
└─ GET /tasks/slow-db (3.11s)
   ├─ PostgreSQL Delay Simulation (3.00s) ← ここが遅い
   │  ├─ Annotation: simulation_type=db-slow
   │  └─ Metadata: delay_seconds=3
   └─ PostgreSQL SELECT tasks (0.05s)
```

### 3. X-Rayサービスマップ

**期待される表示**:

```
[Client] → [ALB] → [ECS FastAPI App] → [PostgreSQL Delay Simulation (3s)]
                                     → [PostgreSQL SELECT tasks (0.05s)]
```

**ノード色**:
- 緑: 正常（レスポンスタイム < 1s）
- 黄: 警告（レスポンスタイム 1-3s）
- 赤: エラー（レスポンスタイム > 3s）

**期待される分析**:
- 「PostgreSQL Delay Simulation」ノードが赤色で表示される
- レスポンスタイムが3秒と表示される
- ボトルネックが一目で分かる

---

## 環境制御設計

### 1. 環境変数

**環境変数名**: `ENABLE_FAULT_SIMULATION`

**値**:

| 値 | 意味 |
|---|-----|
| `true` | 障害シミュレーション有効 |
| `false` | 障害シミュレーション無効（デフォルト） |

**設定場所**:

#### ローカル開発（docker-compose.yml）

```yaml
services:
  app:
    environment:
      - ENABLE_FAULT_SIMULATION=true  # ローカルでは有効
```

#### AWS ECS（タスク定義）

```json
{
  "containerDefinitions": [
    {
      "name": "app",
      "environment": [
        {
          "name": "ENABLE_FAULT_SIMULATION",
          "value": "false"  # 本番では無効
        }
      ]
    }
  ]
}
```

### 2. エンドポイント制御ロジック

**実装コード**:
```python
import os

# モジュールレベルで環境変数を読み込む
ENABLE_FAULT_SIMULATION = os.getenv("ENABLE_FAULT_SIMULATION", "false").lower() == "true"


@router.get("/slow-db", response_model=dict)
async def slow_db_simulation() -> dict:
    # 環境変数チェック（最初に実行）
    if not ENABLE_FAULT_SIMULATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Fault simulation is disabled in this environment"
                }
            },
        )

    # ... 障害シミュレーション処理
```

**エラーレスポンス（無効時）**:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Fault simulation is disabled in this environment"
  }
}
```

**HTTPステータスコード**: `403 Forbidden`

### 3. 環境別の動作

| 環境 | `ENABLE_FAULT_SIMULATION` | 動作 |
|------|-------------------------|------|
| ローカル開発 | `true` | 障害シミュレーション有効（X-Ray検証可能） |
| AWS ECS（開発環境） | `true` | 障害シミュレーション有効（X-Ray検証可能） |
| AWS ECS（本番環境） | `false` | 障害シミュレーション無効（403エラー返却） |

---

## 実装方針

### 1. 修正内容サマリ

| 項目 | 変更内容 | 理由 |
|------|---------|------|
| ルーティング順序 | 具体的なパス → パラメータ付きパス | FastAPIルーティングルール準拠 |
| 環境変数チェック | `ENABLE_FAULT_SIMULATION` 追加 | 本番環境保護 |
| X-Rayサブセグメント | サブセグメント名明確化、Annotation/Metadata追加 | X-Ray可視化強化 |
| エラーハンドリング | 403エラー追加 | 障害シミュレーション無効時のレスポンス |

### 2. 修正ファイル

**ファイルパス**: `src/app/api/tasks.py`

**修正箇所**:
1. モジュールレベルで環境変数読み込み追加
2. ルーティング順序変更（障害シミュレーションエンドポイントを先頭に移動）
3. 各障害シミュレーションエンドポイントに環境変数チェック追加
4. X-Rayサブセグメント強化（Annotation/Metadata追加）

### 3. テスト方法

#### ローカル環境（docker-compose）

**手順**:
```bash
# 1. 環境変数を有効化してコンテナ起動
docker-compose up -d

# 2. 障害シミュレーションAPIテスト
curl http://localhost:8000/tasks/slow-db
curl http://localhost:8000/tasks/slow-logic
curl http://localhost:8000/tasks/slow-external

# 3. X-Rayトレース確認（ローカルX-Ray Daemon経由でAWS X-Rayコンソールへ）
# AWS X-Rayコンソール → Traces → フィルター: Annotation simulation_type=db-slow
```

#### AWS ECS環境（本番）

**手順**:
```bash
# 1. 環境変数を無効化してECSタスク起動（デフォルト）
ALB_DNS="xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com"

# 2. 障害シミュレーションAPI（403エラー確認）
curl http://$ALB_DNS/tasks/slow-db
# 期待レスポンス: 403 Forbidden

# 3. 通常のタスクAPI（正常動作確認）
curl http://$ALB_DNS/tasks
# 期待レスポンス: 200 OK
```

### 4. X-Ray検証手順

**X-Rayコンソール確認項目**:

1. **Service Map**:
   - 障害シミュレーションエンドポイントが独立したノードとして表示されるか
   - レスポンスタイムが遅延時間（3秒、5秒、2秒）と一致するか

2. **Traces**:
   - Annotation `simulation_type` でフィルタリング可能か
   - サブセグメント名が明確か（`PostgreSQL Delay Simulation` 等）

3. **Analytics**:
   - レスポンスタイム分布で遅延が可視化されるか
   - ボトルネックが特定できるか

---

## トラブルシューティング

### 問題1: 障害シミュレーションエンドポイントが404エラー

**原因**: ルーティング順序が誤っている

**対処法**:
1. `src/app/api/tasks.py` のルーティング順序を確認
2. 具体的なパス（`/slow-db`）がパラメータ付きパス（`/{task_id}`）より先に定義されているか確認
3. FastAPIアプリを再起動

### 問題2: 障害シミュレーションエンドポイントが403エラー

**原因**: 環境変数 `ENABLE_FAULT_SIMULATION` が `false` または未設定

**対処法**:
1. 環境変数を確認: `echo $ENABLE_FAULT_SIMULATION`
2. `docker-compose.yml` または ECSタスク定義で環境変数を設定
3. コンテナ再起動

### 問題3: X-Rayトレースが表示されない

**原因**: X-Ray Daemon未起動、IAMロール不足

**対処法**:
1. X-Ray Daemonコンテナが起動しているか確認: `docker ps`
2. ECSタスクロールにX-Ray書き込み権限があるか確認（`xray:PutTraceSegments`）
3. アプリケーションログでX-Rayエラーを確認

### 問題4: 外部API遅延シミュレーションがタイムアウト

**原因**: `httpbin.org` が利用不可、ネットワーク問題

**対処法**:
1. `httpbin.org` の稼働状況を確認: `curl https://httpbin.org/delay/2`
2. ECSタスクからインターネット接続可能か確認（パブリックサブネット、パブリックIP割り当て）
3. タイムアウト値を調整（現在10秒）

---

## 参照ドキュメント

- [API仕様書: 06_api_specification.md](06_api_specification.md) - 障害シミュレーションAPIエンドポイント詳細
- [基本設計: 08_監視・アラート設計.md](../03_基本設計/08_監視・アラート設計.md) - X-Ray監視設計
- [FastAPI公式ドキュメント: Path Operation Configuration](https://fastapi.tiangolo.com/tutorial/path-params/)

---

**作成者**: app-architect (via PM)
**作成日**: 2025-12-14
**バージョン**: 1.0
**レビュー状態**: Draft
