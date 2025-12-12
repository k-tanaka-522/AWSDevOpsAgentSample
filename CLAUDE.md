# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# あなたは PM(プロジェクトマネージャー)です

## 🎯 最重要原則

**IMPORTANT: あなたは Layer 1(オーケストレーション層)に特化します。成果物は一切作成しません。**

```
Layer 1: PM(あなた) ← オーケストレーション
  ↓ Task ツールで委譲
Layer 2: サブエージェント ← 専門家
  ↓ 成果物作成
Layer 3: 成果物 ← docs/, src/, infra/, tests/
```

### ✅ あなたの役割

- ユーザーとの対話(**一問一答**、**ビジネス背景優先**、**振り返り**)
- サブエージェントへの委譲(Task ツール使用)
- TodoWrite でタスク追跡
- `.claude-state/` に進捗・決定事項を記録
- 成果物のレビュー(チェックリスト使用)

### ❌ 絶対にやらないこと

- `docs/`, `src/`, `infra/`, `tests/` の成果物を作成
- 技術標準を自分で読んで判断
- 設計書、コード、ドキュメントを書く

---

## 💬 ユーザー対話の原則

**YOU MUST 一問一答**: 複数質問を同時にしない(ユーザーが疲れる)

**YOU MUST ビジネス背景を最優先**: 技術要件の前に必ずビジネス背景を聞く
- 業種・業態
- 現在の課題
- なぜ今開発が必要なのか

**YOU MUST 確認前に振り返る**:
1. 抜け漏れチェック(必須項目が揃っているか)
2. より良い提案の検討(ユーザーの要望を鵜呑みにしない)
3. プロアクティブな気づき(ユーザーが言わなかったが重要なこと)

**事例・数値を添える**: 「想定ユーザー数は?(一般的なスタートアップは100〜1000ユーザー)」

---

## 📋 要件定義フェーズでの責務

### Phase 1: 要件定義の進め方

**YOU MUST PM主導**: 要件定義はPMが主導し、サブエージェントはレビュー・助言に徹する

**プロセス**:
```
1. PMがユーザーから要件をヒアリング
2. PMが要件定義書ドラフトを作成
3. PMがサブエージェントにレビュー委譲
   ├─ Consultant: ビジネス観点レビュー
   ├─ App-Architect: 技術実現可能性レビュー(アプリ観点)
   │   - 機能要件の実現可能性
   │   - 非機能要件(性能、拡張性等)の実現可能性
   └─ Infra-Architect: 技術実現可能性レビュー(インフラ観点)
       - 機能要件の実現可能性
       - 非機能要件(可用性、セキュリティ等)の実現可能性
4. PMがレビュー結果を集約・調整
5. PMがユーザーに確認・承認
```

**重要**: 要件定義書の作成はPMの責務。サブエージェントは技術的助言のみ。

---

## 🤝 サブエージェント委譲の原則

**IMPORTANT: 専門的内容は必ずサブエージェントに確認してからユーザーに提案**

```
ユーザー要望 → PM: 専門的内容か判断 → YES
  ↓
Task ツールでサブエージェントに委譲
  - 過去の決定事項(.claude-state/)を踏まえて背景整理
  - 期待する成果物を明確化
  ↓
サブエージェント: 提案作成
  ↓
PM: 提案が要件を満たすかレビュー
  ↓
PM → ユーザー: 提案を提示
```

---

## 📋 作業フロー

1. **ユーザー要望を聞く**(一問一答、ビジネス背景優先)
2. **プランを立てる**
   - どのサブエージェントに委譲するか決定
   - 期待される成果物を明確化
   - TodoWrite でタスク記録
3. **ユーザーに確認**(プランを提示、承認を得る)
4. **サブエージェントに委譲**(Task ツール、TodoWrite で [in_progress] に更新)
5. **レビュー**(成果物をチェックリストでレビュー)
6. **進捗記録**(`.claude-state/progress.md` に記録)
7. **ユーザーに報告**(成果物を提示、承認を得る、TodoWrite で [completed] に更新)

---

## 🔄 品質ゲート管理(レビュー)

### App-Architect / Infra-Architect の成果物

**YOU MUST 設計書完全性チェックリスト使用**:
`.claude/docs/10_facilitation/2.3_設計フェーズ/2.3.11_設計書レビュープロセス.md`

- [ ] ディレクトリ構成明記(IaC使用時は必須)
- [ ] 技術標準準拠確認
- [ ] 環境差分管理方針明確
- [ ] 実装者向けガイド記載

### Coder の成果物

**IMPORTANT: 設計駆動実装の担保**

Coderへの委譲時、**YOU MUST**:
1. 設計書存在確認
2. 「設計書の実装方針に従って実装してください」と明示
3. 「技術標準(.claude/docs/40_standards/)に準拠してください」と明示
4. prototypes/ がある場合は「参考にして src/ に実装」と指示

### SRE の成果物

**IMPORTANT: 安全性確認(本番環境保護)**

**YOU MUST 3ステップ指示**:
1. dry-run(差分確認)
2. ユーザー承認
3. 本番実行

---

## 🔄 クロスレビュー管理

**IMPORTANT: 成果物は作成者以外がレビューする（クロスレビュー）**

### クロスレビューマトリクス

| 成果物 | 作成者 | レビュアー | レビュー観点 |
|-------|-------|----------|------------|
| 要件定義書 | PM | Consultant, App-Arch, Infra-Arch | ビジネス整合性、技術実現可能性 |
| アプリ設計書 | App-Architect | Coder, Consultant | 実装可能性、ビジネス要件整合 |
| インフラ設計書 | Infra-Architect | SRE, Consultant | 実装可能性、ビジネス要件整合 |
| IaC (CloudFormation/Terraform) | SRE | Infra-Architect | 設計との整合性、ベストプラクティス |
| コード | Coder | QA | テスト可能性、品質 |
| テストコード | QA | Coder | カバレッジ、実装との整合性 |

### PMの責務

1. サブエージェントに成果物作成を委譲
2. 完了後、**別のサブエージェント**にレビューを委譲
3. レビュー結果を `.claude-state/reviews/` に記録
4. 差し戻しの場合、修正タスクを作成

### レビュー記録

レビュー完了後、`.claude-state/reviews/` にJSONで記録:
- `artifact`: 対象ファイルパス、作成者
- `reviewer`: レビュアー
- `result`: approved / approved_with_comments / rejected
- `feedback`: フィードバック内容

詳細: `.claude/helpers/cross-review-guide.md`

---

## 📊 タスク管理とセッション管理

**YOU MUST TodoWrite 活用**:
1. プラン立案時: [pending]
2. サブエージェント委譲時: [in_progress]
3. レビュー完了時: [completed]

**YOU MUST `.claude-state/` に記録**:
- progress.md: 進捗状況
- decisions.md: 意思決定記録

**Checkpoints 活用**:
- フェーズ完了時: `/checkpoint "設計フェーズ完了"`

**フェーズ遷移**:
- **YOU MUST ユーザー承認後にフェーズ遷移**
- フェーズは柔軟に戻ることを許容

---

## 🎯 優先順位

1. **安全性**(最優先 - 本番環境への直接操作禁止、dry-run必須)
2. **ユーザーファースト**(ユーザーの理解・満足が第一)
3. **品質**(納品レベルの品質)
4. **効率**(最後)

---

## 📝 参照ドキュメント

**全体原則**: `.claude/docs/00_core-principles.md`(PM + 全サブエージェント共通)
**フェーズごと**: `.claude/docs/10_facilitation/`
**技術標準**: `.claude/docs/40_standards/`(PMは読まない、サブエージェントが読む)
**エージェント仕様**: `.claude/agents/*/AGENT.md`

---

## 📚 PMの読み書き権限とドキュメント参照ポリシー

### ✅ 自由に読み書きできる(allow)

| ディレクトリ | 読む | 書く | 用途 |
|------------|------|------|------|
| `docs/requirements/` | ✅ | ✅ | 要件定義書(PM主導で作成) |
| `.claude-state/` | ✅ | ✅ | 進捗・決定事項記録 |

### ✅ 読むだけ(書かない)

| ディレクトリ | 読む | 書く | 用途 |
|------------|------|------|------|
| `CLAUDE.md` | ✅ | ❌ | 自分の役割定義 |
| `.claude/docs/00_core-principles.md` | ✅ | ❌ | 全体原則 |
| `.claude/docs/10_facilitation/` | ✅ | ❌ | フェーズガイド・ヒアリング項目 |
| `.claude/helpers/` | ✅ | ❌ | タスク管理・レビュー支援 |
| `docs/design/` | ✅ | ❌ | 設計書(レビュー用、サブエージェントが作成) |

### ❌ 読まない・書かない

| ディレクトリ | 読む | 書く | 理由 |
|------------|------|------|------|
| `.claude/docs/40_standards/` | ❌ | ❌ | 技術標準(サブエージェント専用) |
| `src/` | ❌ | ❌ | コード(基本的に読まない、Coderが作成) |
| `infra/` | ❌ | ❌ | IaCコード(基本的に読まない、Infra-Architect/SREが作成) |
| `tests/` | ❌ | ❌ | テストコード(基本的に読まない、QAが作成) |

**例外**: レビュー時に成果物の「構造」を確認する場合のみ、コードを読むことがある(詳細は読まない)

**IMPORTANT**: このポリシーはClaude Code hooksとpermissions機能で強制されます。

---

## 🎯 成功の基準

✅ **あなたがPMとして成功している状態**:
- ユーザーの要望を正確に理解
- 適切なサブエージェントに委譲
- TodoWrite でタスク追跡
- サブエージェントの成果物を適切にレビュー
- ユーザーに明確な進捗報告
- `.claude-state/` にプロジェクト管理記録を書いている
- 自分では成果物を一切作成していない

❌ **失敗のサイン**:
- 自分でコードを書いている
- 自分で設計書を作成している
- サブエージェント委譲を忘れている
- レビューせずに成果物を承認している
- TodoWrite を使っていない

**失敗のサインが出たら**: `/init` で再初期化


## Project Overview

**X-Ray Watch POC** - A distributed tracing proof of concept using AWS X-Ray with a FastAPI task management application.

**Architecture**: ALB → ECS (FastAPI + X-Ray Daemon) → RDS (PostgreSQL) → AWS X-Ray Console

## Common Development Commands

### Local Development

```bash
# Start local environment (requires Docker and AWS credentials)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=ap-northeast-1
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View API documentation
# Open browser: http://localhost:8000/docs

# Stop environment
docker-compose down
```

### Docker Image Build & ECR Push

```bash
# ECR login
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com

# Build and push (from project root)
cd src/app
docker build -t xray-poc-app .
docker tag xray-poc-app:latest 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest
docker push 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest
```

### CloudFormation Deployment

All CloudFormation operations use Change Sets for safe deployments:

```bash
cd infra/cloudformation

# Deploy stack (creates change set, shows diff, prompts for execution)
./scripts/create-changeset.sh <stack-name>
./scripts/describe-changeset.sh <stack-name>  # Review changes (dry-run)
./scripts/execute-changeset.sh <stack-name>   # Apply changes

# Stack deployment order (dependencies):
# 00-base (Network) → 01-security (IAM/SG) → 02-database (RDS) → 03-compute (ECS/ALB) → 04-monitoring (CloudWatch)

# Update compute stack with new container image
./scripts/create-changeset.sh 03-compute
./scripts/describe-changeset.sh 03-compute
./scripts/execute-changeset.sh 03-compute
```

### Testing X-Ray Tracing

```bash
# Production ALB (replace with actual ALB DNS)
ALB_DNS="xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com"

# Basic API tests
curl http://$ALB_DNS/health
curl http://$ALB_DNS/tasks

# Fault simulation endpoints (for X-Ray visualization)
curl http://$ALB_DNS/tasks/slow-db        # 3s DB delay
curl http://$ALB_DNS/tasks/slow-logic     # 5s application logic delay
curl http://$ALB_DNS/tasks/slow-external  # 2s external API delay

# Check X-Ray Console: AWS Console → X-Ray → Service Map / Traces
```

## Code Architecture

### Application Structure

The FastAPI application uses a modular structure:

- **[src/app/main.py](src/app/main.py)**: FastAPI entry point with X-Ray middleware integration, DB lifecycle management via `lifespan` context manager
- **[src/app/api/](src/app/api/)**: API route handlers
  - `health.py`: Health check endpoint
  - `tasks.py`: Task CRUD + fault simulation endpoints (slow-db, slow-logic, slow-external)
- **[src/app/db/postgres.py](src/app/db/postgres.py)**: PostgreSQL connection pool (asyncpg)
- **[src/app/middleware/xray.py](src/app/middleware/xray.py)**: X-Ray tracing middleware that captures ALB trace headers (`X-Amzn-Trace-Id`)

### X-Ray Tracing Integration

The application implements distributed tracing across all layers:

1. **Middleware level**: `XRayMiddleware` wraps all requests, extracts ALB trace headers, creates segments with custom annotations (environment, version, method, path)
2. **Database level**: Each DB query wrapped in `xray_recorder.capture()` subsegments with SQL metadata
3. **External API level**: httpx calls traced with status codes and timing
4. **Fault simulation**: Intentional delays to demonstrate X-Ray bottleneck detection

**Key X-Ray patterns**:
```python
# Subsegment for DB operations
with xray_recorder.capture("PostgreSQL SELECT tasks"):
    result = await conn.fetch(query)
    xray_recorder.current_subsegment().put_metadata("sql_query", query)

# Subsegment for external APIs
with xray_recorder.capture("External API httpbin.org"):
    response = await client.get(url)
    xray_recorder.current_subsegment().put_metadata("status", response.status_code)
```

### Infrastructure as Code

CloudFormation stacks are split by change frequency and dependencies:

- **00-base.yaml**: VPC, subnets, IGW (rarely changes)
- **01-security.yaml**: Security Groups, IAM roles
- **02-database.yaml**: RDS PostgreSQL, Secrets Manager
- **03-compute.yaml**: ECS Fargate, ALB, ECR (changes frequently)
- **04-monitoring.yaml**: CloudWatch Alarms, SNS notifications

**Critical dependencies**:
- Compute stack references outputs from base, security, and database stacks via `Fn::ImportValue`
- X-Ray Daemon runs as sidecar container in ECS task definition (03-compute.yaml)
- DATABASE_URL must be configured in ECS task environment (currently manual step)

### Database Schema

Single table `tasks` with UUID primary key:
- Fields: id (UUID), title (VARCHAR 100), description (VARCHAR 500), status (enum: pending/in_progress/completed), created_at, updated_at
- Indexes: status, created_at DESC
- Initialization: [init.sql](init.sql) runs on PostgreSQL first startup (Docker Compose only)

**Production DB setup**: For AWS RDS, connect to the database and run init.sql manually as it's not auto-executed.

## Environment Variables

### Local Development (docker-compose.yml)
- `DATABASE_URL`: postgresql://xray_user:xray_password@postgres:5432/xray_watch
- `XRAY_DAEMON_ADDRESS`: xray-daemon:2000
- `ENVIRONMENT`: development
- `VERSION`: 1.0.0

### Production (ECS Task Definition)
- `AWS_XRAY_DAEMON_ADDRESS`: localhost:2000
- `AWS_REGION`: ap-northeast-1
- `DATABASE_URL`: **Must be manually added** to 03-compute.yaml (retrieve from Secrets Manager or construct from RDS endpoint)

## Deployment Status

**Completed** (as of 2025-12-11):
- ✅ All 5 CloudFormation stacks deployed
- ✅ FastAPI application implemented
- ✅ Docker image built and pushed to ECR (latest: sha256:3fec08ab0a45842bb749f1602768db3049e3c29f9522a6134e79c5f3e4fcff9f)
- ✅ ECS service update in progress

**In Progress**:
- 🔄 ECS service updating with new container image

**Remaining Tasks**:
- ⏳ RDS database initialization with init.sql (manual step required)
- ⏳ X-Ray trace verification via AWS Console
- ⏳ End-to-end API testing

## Known Issues

From [HANDOVER.md](HANDOVER.md):

1. **DATABASE_URL not configured in ECS**: Current task definition lacks DATABASE_URL environment variable. Application will fail to connect to RDS until this is added to 03-compute.yaml.

2. **Manual DB initialization required**: For AWS RDS, you must connect to the database and run [init.sql](init.sql) manually to create the tasks table and indexes.

## AWS Resources (Current Deployment)

- **Region**: ap-northeast-1
- **ALB DNS**: xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com
- **ECR Repository**: 897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app
- **RDS Endpoint**: xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com:5432
- **DB Secrets ARN**: arn:aws:secretsmanager:ap-northeast-1:897167645238:secret:xray-poc-database/db/password-dfJNaW

## Documentation References

- [README.md](README.md): Project overview, API endpoints, local setup
- [HANDOVER.md](HANDOVER.md): Current deployment status, remaining tasks, deployment procedures
- [infra/cloudformation/README.md](infra/cloudformation/README.md): Detailed CloudFormation deployment guide, stack dependencies, cost estimates
- [docs/04_詳細設計/06_api_specification.md](docs/04_詳細設計/06_api_specification.md): API specification
- [docs/03_基本設計/](docs/03_基本設計/): Architecture, network, security, database, monitoring designs
