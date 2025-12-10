# CloudFormation Templates - X-Ray Watch POC

## 概要

AWS X-Ray Watch POC のインフラストラクチャを CloudFormation で管理します。

### スタック構成（5スタック）

| スタック | 変更頻度 | 含まれるリソース | デプロイ戦略 |
|---------|--------|----------------|------------|
| 00-base | 年1回 | VPC、サブネット、IGW | 手動、複数人承認 |
| 01-security | 月1回 | Security Groups、IAMロール | 手動、1人承認 |
| 02-database | 月1回 | RDS、Secrets Manager | 手動、1人承認 |
| 03-compute | 週数回 | ECS、ALB、ECR | 自動（CI/CD） |
| 04-monitoring | 月1回 | CloudWatch、SNS | 手動、1人承認 |

### 依存関係

```
00-base (Network)
  ↓
01-security (Security Groups, IAM)
  ↓
02-database (RDS) ← 01-security
  ↓
03-compute (ECS, ALB) ← 00-base, 01-security, 02-database
  ↓
04-monitoring (CloudWatch) ← 02-database, 03-compute
```

## ディレクトリ構造

```
infra/cloudformation/
├── stacks/                    # スタック定義（5ファイル）
│   ├── 00-base.yaml          # Network Stack
│   ├── 01-security.yaml      # Security Stack
│   ├── 02-database.yaml      # Database Stack
│   ├── 03-compute.yaml       # Compute Stack
│   └── 04-monitoring.yaml    # Monitoring Stack
│
├── parameters/                # 環境差分パラメータ
│   └── dev.json              # 開発環境パラメータ
│
├── scripts/                   # デプロイスクリプト
│   ├── create-changeset.sh   # Change Set作成
│   ├── describe-changeset.sh # Change Set詳細表示（dry-run）
│   ├── execute-changeset.sh  # Change Set実行
│   └── delete-stack.sh       # スタック削除
│
└── README.md                  # このファイル
```

## 前提条件

### 必須ツール

- AWS CLI v2
- jq（JSONパーサー）
- Bash（Linux/macOS/WSL）

### AWS認証情報

```bash
# AWS CLIプロファイル設定
aws configure

# 認証確認
aws sts get-caller-identity
```

### パラメータファイル編集

`parameters/dev.json` を編集して以下を設定：

```json
{
  "ParameterKey": "AlertEmail",
  "ParameterValue": "your-email@example.com"  # ← あなたのメールアドレスに変更
}
```

## デプロイ方法

### 初回デプロイ（全スタック）

**手順**:

```bash
cd infra/cloudformation

# 1. Network Stack（00-base）
./scripts/create-changeset.sh 00-base
./scripts/describe-changeset.sh 00-base  # 差分確認（dry-run）
./scripts/execute-changeset.sh 00-base   # 実行（yes入力）

# 2. Security Stack（01-security）
./scripts/create-changeset.sh 01-security
./scripts/describe-changeset.sh 01-security
./scripts/execute-changeset.sh 01-security

# 3. Database Stack（02-database）
./scripts/create-changeset.sh 02-database
./scripts/describe-changeset.sh 02-database
./scripts/execute-changeset.sh 02-database

# 4. Compute Stack（03-compute）
./scripts/create-changeset.sh 03-compute
./scripts/describe-changeset.sh 03-compute
./scripts/execute-changeset.sh 03-compute

# 5. Monitoring Stack（04-monitoring）
./scripts/create-changeset.sh 04-monitoring
./scripts/describe-changeset.sh 04-monitoring
./scripts/execute-changeset.sh 04-monitoring
```

### デプロイ所要時間

| スタック | 作成時間 | 更新時間 |
|---------|---------|---------|
| 00-base | 2分 | 1分 |
| 01-security | 1分 | 30秒 |
| 02-database | 10分 | 5分 |
| 03-compute | 5分 | 3分 |
| 04-monitoring | 1分 | 30秒 |
| **合計** | **約20分** | **約10分** |

### スタック更新（変更デプロイ）

```bash
# 例: Compute Stackのタスク定義を変更
vim stacks/03-compute.yaml

# Change Set作成
./scripts/create-changeset.sh 03-compute

# 差分確認（dry-run）
./scripts/describe-changeset.sh 03-compute

# 実行
./scripts/execute-changeset.sh 03-compute
```

### スタック削除

**注意**: 依存関係の逆順で削除してください。

```bash
# 1. Monitoring Stack削除
./scripts/delete-stack.sh 04-monitoring

# 2. Compute Stack削除
./scripts/delete-stack.sh 03-compute

# 3. Database Stack削除
./scripts/delete-stack.sh 02-database

# 4. Security Stack削除
./scripts/delete-stack.sh 01-security

# 5. Network Stack削除
./scripts/delete-stack.sh 00-base
```

## よくある変更

| やりたいこと | 編集するファイル | デプロイするスタック |
|------------|----------------|-------------------|
| VPC CIDRを変更 | `parameters/dev.json` | 00-base |
| RDSインスタンスクラス変更 | `parameters/dev.json` | 02-database |
| ECSタスク定義変更 | `stacks/03-compute.yaml` | 03-compute |
| アラート閾値変更 | `stacks/04-monitoring.yaml` | 04-monitoring |
| メール通知先変更 | `parameters/dev.json` | 04-monitoring |

## トラブルシューティング

### Change Set作成失敗

**原因**: 依存スタックが未デプロイ

**対処法**: 依存関係順にデプロイ（00 → 01 → 02 → 03 → 04）

```bash
# 依存スタック確認
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --region ap-northeast-1 \
  --query 'StackSummaries[?contains(StackName, `xray-poc`)].StackName' \
  --output table
```

### スタック作成失敗（IAMロール）

**原因**: `CAPABILITY_NAMED_IAM` 未指定

**対処法**: スクリプトは自動的に `--capabilities CAPABILITY_NAMED_IAM` を付与します。手動実行時は注意。

### RDS作成タイムアウト

**原因**: RDS作成は10分程度かかる

**対処法**: 待つ（正常動作）

### メール通知が来ない

**原因**: SNS Subscriptionの確認メールを承認していない

**対処法**:

1. メール受信トレイを確認
2. 「AWS Notification - Subscription Confirmation」メールを探す
3. 「Confirm subscription」リンクをクリック

## Change Sets のメリット

**安全性**:
- デプロイ前に差分確認（dry-run）
- 意図しない削除を防止
- ロールバックが容易

**例**:

```bash
# Change Set確認（dry-run）
./scripts/describe-changeset.sh 02-database

# 出力例:
# Action: Modify
# LogicalId: DBInstance
# Type: AWS::RDS::DBInstance
# Replacement: True  # ← インスタンス再作成（ダウンタイムあり）
```

→ `Replacement: True` の場合、慎重に判断

## コスト試算

### 月額コスト（POC構成）

| リソース | スペック | 月額コスト（USD） |
|---------|---------|-----------------|
| RDS PostgreSQL | db.t4g.micro, 20GB | $15 |
| ECS Fargate | 0.25vCPU, 0.5GB, 1タスク | $12 |
| ALB | 1台 | $20 |
| CloudWatch | Logs 1GB, Alarms 10個 | $5 |
| NAT Gateway | なし | $0 |
| X-Ray | トレース 1000万件/月 | $5 |
| **合計** | - | **約$57/月** |

### コスト削減のヒント

- **夜間停止**: RDS/ECSを夜間停止で50%削減
- **スポットインスタンス**: ECSをSpot割引で30%削減（本番非推奨）
- **ログ保持期間短縮**: CloudWatch Logsを3日間に短縮

## 参照ドキュメント

- [基本設計: 10_IaC構成方針.md](../../docs/03_基本設計/10_IaC構成方針.md)
- [詳細設計: INDEX.md](../../docs/04_詳細設計/INDEX.md)
- [CloudFormation技術標準](../../.claude/docs/40_standards/42_infra/iac/cloudformation.md)

---

**作成者**: SRE Team (via PM)
**作成日**: 2025-12-10
**バージョン**: 1.0.0
