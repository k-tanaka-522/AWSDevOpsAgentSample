# 実装フェーズ実行ガイド（PHASE_GUIDE）

## このドキュメントの目的

**Claude（あなた）が実装フェーズを実行するための唯一のエントリーポイント**

- ユーザーとの一問一答で実装フェーズを進める
- PDCA 2周でコード生成・レビュー・改善
- 実装完了して次フェーズへ遷移

**重要**: このファイルを読めば、実装フェーズで何をすべきか全てわかります。他のファイルは参照用です。

---

## §1 このフェーズでやること（What）

### 1.1 実装フェーズの目的

**基本設計書を受けて、システムを実装する**

- **Input**: 基本設計書（`docs/03_基本設計書.md` または `docs/03_基本設計書/`）
- **Output**: 実装コード（`src/`、`tests/`、`infra/` 等）
- **成果物の品質**: 受託開発納品レベル（テスト済み、本番デプロイ可能）

### 1.2 実装フェーズで生成すること

以下を**すべて**生成します（省略禁止）:

#### A. アプリケーションコード
- [ ] ソースコード（`src/`）
- [ ] テストコード（`tests/`）
- [ ] 設定ファイル（`.env.example`、`config/` 等）

#### B. インフラコード（IaC）
- [ ] CloudFormation または Terraform
- [ ] デプロイスクリプト（`scripts/deploy.sh` 等）

#### C. ドキュメント
- [ ] README.md（セットアップ手順、実行方法）
- [ ] CONTRIBUTING.md（開発者向けガイド）
- [ ] API仕様書（Swagger/OpenAPI）

#### D. CI/CDパイプライン
- [ ] GitHub Actions または GitLab CI
- [ ] テスト自動化
- [ ] デプロイ自動化

### 1.3 実装フェーズの制約

- **基本設計書との整合性**: すべての実装は基本設計書に基づく
- **技術標準の遵守**: `.claude/docs/40_standards/` の技術標準を必ず参照
- **コード品質**: テストカバレッジ80%以上、静的解析エラーゼロ

---

## §2 技術標準参照

### 2.1 参照すべき技術標準

実装時には、以下の技術標準を**必ず参照**してください:

| 技術標準ファイル | 参照タイミング | 必須度 |
|----------------|--------------|--------|
| `.claude/docs/40_standards/41_python.md` | Python実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/42_typescript.md` | TypeScript実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/43_csharp.md` | C#実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/44_go.md` | Go実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/45_cloudformation.md` | CloudFormation実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/46_terraform.md` | Terraform実装時 | ⭐⭐⭐ 必須 |
| `.claude/docs/40_standards/49_security.md` | すべての実装 | ⭐⭐⭐ 必須 |

### 2.2 技術標準の適用方針

**技術標準は厳守**（設計で決定したら、実装は技術標準に従う）

---

## §3 PDCA 1周目（コード生成）

### 3.1 Plan（計画）

**基本設計書を読み込んで、実装計画を立てる**

#### ステップ1: 基本設計書の読み込み

```bash
# 基本設計書を読み込む
docs/03_基本設計書.md または docs/03_基本設計書/
```

**確認すべき項目:**
- [ ] アーキテクチャパターン
- [ ] 技術スタック
- [ ] ディレクトリ構成
- [ ] IaC方針

#### ステップ2: 実装順序の決定

**ユーザーへの質問例:**

> 「基本設計書を確認しました。実装を開始します。
>
> 実装順序の提案:
>
> 1. **インフラ構築**（CloudFormation）
>    - VPC、Subnet、Security Groups
>    - ECS Cluster、ALB
>
> 2. **アプリケーション実装**（Python/FastAPI）
>    - データモデル（models/）
>    - API実装（routers/）
>    - テストコード（tests/）
>
> 3. **CI/CDパイプライン**（GitHub Actions）
>    - テスト自動化
>    - デプロイ自動化
>
> この順序で進めて問題ないですか？または、優先順位を変更しますか？」

### 3.2 Do（実行）

**技術標準を参照しながらコードを生成する**

#### コード生成の原則

**事前説明 → 生成 → 事後説明**

1. **事前説明**: これから生成するコードの概要を説明
2. **生成**: コードを生成
3. **事後説明**: 生成したコードのポイント、ベストプラクティスを説明

**例:**

> 「**事前説明:**
> これから、FastAPIのデータモデルを生成します。
> Pydanticを使って、型ヒント・バリデーションを実装します。
>
> （コード生成）
>
> **事後説明:**
> 生成したコードのポイント:
> - Pydanticの`BaseModel`を継承して型ヒント
> - `Field`でバリデーション（最小値、最大値、必須/任意）
> - `Config`でJSON Schema生成（Swagger対応）
>
> 技術標準 41_python.md の「型ヒント必須」に準拠しています。」

### 3.3 Check（確認）

**生成したコードを確認する**

**確認すべき項目:**
- [ ] 技術標準に準拠しているか
- [ ] テストコードがあるか
- [ ] ドキュメント（docstring、コメント）があるか

### 3.4 Act（改善）

**不足している項目を追加生成**

**例:**

> 「データモデルが完成しました。次に、API実装に進みますか？
> または、先にテストコードを生成しますか？」

---

## §4 PDCA 2周目（レビュー・改善）

### 4.1 Plan（計画）

**1周目で生成したコードをレビューする**

**確認すべき項目:**
- [ ] テストが通るか（`pytest`、`jest` 等）
- [ ] 静的解析エラーがないか（`mypy`、`eslint` 等）
- [ ] テストカバレッジが80%以上か

### 4.2 Do（実行）

**テスト・静的解析を実行**

**例:**

> 「コード生成が完了しました。テストを実行します。
>
> ```bash
> pytest tests/ --cov=src --cov-report=html
> ```
>
> 実行結果:
> - テスト: 15件実行、すべてパス
> - カバレッジ: 85%
>
> 問題ありません。次に、静的解析を実行します。」

### 4.3 Check（確認）

**実装完了条件のチェック**

#### チェックリスト

**A. コード品質**
- [ ] テストがすべてパス
- [ ] テストカバレッジ80%以上
- [ ] 静的解析エラーゼロ

**B. 基本設計書との整合性**
- [ ] すべての機能が実装されている
- [ ] アーキテクチャパターンに準拠

**C. ドキュメント**
- [ ] README.mdがある
- [ ] API仕様書がある

### 4.4 Act（改善）

**「もっといい提案」を準備**

**ユーザーへの提案例:**

> 「実装が完了しました。ここまでの内容を振り返ると、以下のような改善案があります:
>
> 1. **パフォーマンス最適化**: データベースクエリにインデックス追加
>    - 効果: レスポンスタイム50%改善
>
> 2. **エラーハンドリング強化**: リトライ処理追加
>    - 効果: 外部API障害時の可用性向上
>
> これらを実装しますか？または、現在の実装で進めますか？」

---

## §5 デプロイ準備

### 5.1 デプロイ準備の手順

#### ステップ1: デプロイスクリプト生成

**参照ドキュメント**: `2.4.6.1.7_デプロイ自動化設計.md`

**必須スクリプト:**
- `scripts/deploy.sh` - デプロイ自動化
- `scripts/validate.sh` - テンプレート検証
- `scripts/rollback.sh` - ロールバック

#### ステップ2: CI/CDパイプライン設定

**GitHub Actions例:**

```yaml
name: Deploy to AWS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      - name: Deploy to AWS
        run: ./scripts/deploy.sh dev
```

#### ステップ3: 環境変数設定

**`.env.example` 生成:**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp

# AWS
AWS_REGION=ap-northeast-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### 5.2 デプロイ準備完了確認

**ユーザーへの確認:**

> 「デプロイ準備が完了しました。
>
> **デプロイ可能な環境:**
> - dev環境: `./scripts/deploy.sh dev`
> - prod環境: `./scripts/deploy.sh prod`
>
> デプロイを実行しますか？または、テストフェーズに進みますか？」

---

## §6 次フェーズへの遷移判定

### 6.1 実装フェーズ完了条件

以下がすべて満たされたら、テストフェーズへ遷移できます:

#### A. コード生成完了
- [ ] アプリケーションコード（`src/`、`tests/`）が存在する
- [ ] インフラコード（`infra/`、`scripts/`）が存在する

#### B. コード品質
- [ ] テストがすべてパス
- [ ] テストカバレッジ80%以上
- [ ] 静的解析エラーゼロ

#### C. ドキュメント
- [ ] README.mdがある
- [ ] API仕様書がある

#### D. デプロイ準備
- [ ] デプロイスクリプトがある
- [ ] CI/CDパイプラインが設定されている

### 6.2 次フェーズへの遷移

**ユーザーへの確認:**

> 「実装が完了しました。
>
> **実装した内容:**
> - アプリケーションコード: `src/`、`tests/`
> - インフラコード: `infra/cloudformation/`
> - デプロイスクリプト: `scripts/deploy.sh`
> - CI/CDパイプライン: `.github/workflows/deploy.yml`
>
> **コード品質:**
> - テスト: すべてパス
> - カバレッジ: 85%
> - 静的解析: エラーゼロ
>
> テストフェーズに進んで、統合テストを実施しますか？」

**プロジェクト状態の更新:**

```json
{
  "projectName": "プロジェクト名",
  "currentPhase": "testing",
  "status": "ongoing",
  "completedPhases": ["planning", "requirements", "design", "implementation"],
  "updatedAt": "2025-10-24T12:00:00Z"
}
```

---

## 📚 参考資料

### 実装フェーズの詳細プロセス

以下のファイルは、必要に応じて参照してください（必須ではありません）:

| ファイル | 内容 | 参照タイミング |
|---------|------|---------------|
| `2.4.5_言語別コーディング規約適用/` | 言語別の実装ガイド | コード生成時 |
| `2.4.6_IaC構築プロセス/` | IaC実装ガイド | インフラコード生成時 |
| `2.4.6.1.7_デプロイ自動化設計.md` | デプロイスクリプト設計 | デプロイ準備時 |

---

## 🚨 重要な注意事項

### 1. 事前説明 → 生成 → 事後説明

**コード生成時は、必ず説明を付ける**

✅ Good:
> 「**事前説明:**
> これから、FastAPIのエンドポイントを生成します。
>
> （コード生成）
>
> **事後説明:**
> 技術標準 41_python.md の「型ヒント必須」に準拠しています。」

### 2. 技術標準は厳守

**実装は技術標準に従う**

✅ 技術標準を参照してから実装
❌ 技術標準を参照せずに実装

### 3. テストは必須

**すべてのコードにテストコードを生成**

✅ Good:
```
src/
  models/
    user.py
tests/
  models/
    test_user.py  # 必ずテストコードを生成
```

### 4. デプロイスクリプトは必須

**CloudFormation/Terraformだけでなく、デプロイスクリプトも生成**

**⭐⭐⭐ 最重要: CloudFormation の場合は Change Set スクリプト必須**

✅ Good（CloudFormation）:
```
infra/cloudformation/
  stacks/
    network/
      main.yaml
scripts/
  create-changeset.sh      # Change Set 作成（dry-run）⭐必須
  describe-changeset.sh    # Change Set 内容確認 ⭐必須
  execute-changeset.sh     # ユーザー承認後に実行 ⭐必須
  rollback.sh              # ロールバック処理 ⭐必須
```

**禁止事項**:
❌ Bad: `aws cloudformation deploy` による直接デプロイは禁止
- 本番環境での安全性が確保できない
- dry-run（変更内容の事前確認）ができない

**必ず Change Set を使う理由**:
1. 本番環境への影響を事前に確認できる（dry-run）
2. ユーザーが変更内容を承認してから実行できる
3. ロールバックが容易

**参照**: `.claude/docs/40_standards/45_cloudformation.md` の「デプロイ手順（Change Sets必須）」セクション

✅ Good（Terraform）:
```
infra/terraform/
  main.tf
scripts/
  plan.sh      # terraform plan（dry-run）
  apply.sh     # terraform apply
  rollback.sh
```

---

**作成日**: 2025-10-24
**対象フェーズ**: 実装
**重要度**: ⭐⭐⭐ 最重要
