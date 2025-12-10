# GitHub Actions 標準

## 概要

本ドキュメントは、GitHub Actions を使用した CI/CD パイプラインの標準を定義します。

**対象**:
- CloudFormation デプロイパイプライン
- Terraform デプロイパイプライン
- アプリケーションCI/CD（TypeScript, Python等）

**検証状況**:
- ✅ CloudFormation + OIDC認証: 検証完了（2025-10-26）
- ⏳ Terraform: 未検証
- ⏳ アプリケーションCI/CD: 未検証

---

## 基本原則

### 1. OIDC認証を使用

GitHub Actions から AWS へのアクセスは**OIDC (OpenID Connect) 認証**を使用し、長期的な認証情報（Access Key/Secret Key）を使用しない。

**理由**:
- シークレットの漏洩リスクを排除
- IAM ロールでリポジトリ単位の権限制御
- 一時的な認証情報で安全性向上

**参考**: [検証完了レポート - OIDC認証セットアップ](../../../../../../sampleAWS-subagent/docs/90_運用手順/00_検証完了レポート.md#1-oidc認証セットアップ)

---

### 2. PR時はプレビュー、マージ後はデプロイ

| イベント | アクション | 目的 |
|---------|----------|------|
| Pull Request作成 | `preview` ジョブ: Change Set作成 + PRコメント | レビュー時に変更内容を確認 |
| `main` ブランチマージ | `deploy` ジョブ: Change Set実行 | 自動デプロイ |

**Branch Protection Rules** と組み合わせて、承認なしのデプロイを防止。

---

### 3. パラメーターフィルタリング

CloudFormation デプロイ時、全スタック共通のパラメーターファイル（`dev.json`, `stg.json`等）から、**各スタックに必要なパラメーターのみを動的に抽出**する。

**理由**:
- 不要なパラメーターを渡すとエラーになる
  ```
  Parameters: [VendorApiDesiredCount, ...] do not exist in the template
  ```
- スタックごとにパラメーターファイルを分けると管理が煩雑

**解決策**: jq + `aws cloudformation get-template-summary` でフィルタリング

**参考**: [検証完了レポート - パラメーターフィルタリング](../../../../../../sampleAWS-subagent/docs/90_運用手順/00_検証完了レポート.md#3-パラメーターフィルタリング)

---

### 4. 環境別デプロイ戦略

| 環境 | トリガー | 承認 | デプロイタイミング |
|-----|---------|------|------------------|
| dev | `main` マージ | 不要 | 自動（即時） |
| stg | `release/stg` マージ | 1人承認 | 手動トリガー（GitHub UI） |
| prd | `release/prd` マージ | 2人承認 | 手動トリガー（GitHub UI） |

**Branch Protection Rules**:
- `main`: 1人承認 + `preview` ジョブ成功必須
- `release/stg`: 1人承認 + `preview` ジョブ成功必須
- `release/prd`: 2人承認 + `preview` ジョブ成功必須 + CODEOWNERS設定

---

## CloudFormation デプロイパイプライン

### 推奨ワークフロー構造

```yaml
name: CloudFormation Deploy

on:
  pull_request:
    branches: [main]
    paths:
      - 'infra/cloudformation/**'
      - '.github/workflows/cloudformation-deploy.yml'

  push:
    branches: [main]
    paths:
      - 'infra/cloudformation/**'
      - '.github/workflows/cloudformation-deploy.yml'

# OIDC認証用の権限
permissions:
  id-token: write      # OIDC認証に必要
  contents: read       # リポジトリ読み取り
  pull-requests: write # PRコメント投稿

jobs:
  preview:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-northeast-1

      - name: Create Change Sets
        # ... (後述)

      - name: Comment PR
        uses: actions/github-script@v7
        # ... (後述)

  deploy:
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ap-northeast-1

      - name: Deploy Stacks
        # ... (後述)
```

---

### OIDC認証セットアップ

#### 1. AWS側の設定

**スクリプトで自動化** (推奨):

```bash
#!/bin/bash
# scripts/setup-github-oidc.sh

REPO_OWNER="your-org"
REPO_NAME="your-repo"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 1. OIDC Provider作成
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
  --tags Key=ManagedBy,Value=CloudFormation

# 2. IAM Role作成
cat > /tmp/trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${REPO_OWNER}/${REPO_NAME}:*"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  --tags Key=ManagedBy,Value=Terraform

# 3. IAM Policy作成・アタッチ
cat > /tmp/policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "ec2:*",
        "ecs:*",
        "rds:*",
        "elasticloadbalancing:*",
        "cognito-idp:*",
        "logs:*",
        "cloudwatch:*",
        "sns:*",
        "iam:*",
        "kms:*",
        "secretsmanager:*",
        "cloudfront:*",
        "ssm:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name GitHubActionsCloudFormationPolicy \
  --policy-document file:///tmp/policy.json

aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/GitHubActionsCloudFormationPolicy

# 4. GitHub Secretに Role ARN を設定
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/GitHubActionsDeployRole"

gh secret set AWS_DEPLOY_ROLE_ARN \
  --body "$ROLE_ARN" \
  --repo ${REPO_OWNER}/${REPO_NAME}

echo "✅ OIDC Setup Complete!"
echo "Role ARN: $ROLE_ARN"
```

**実行**:
```bash
chmod +x scripts/setup-github-oidc.sh
./scripts/setup-github-oidc.sh
```

**検証済み**: [Sample-AWS-SubAgent](https://github.com/k-tanaka-522/Sample-AWS-SubAgent) で動作確認済み

---

#### 2. GitHub Actions での使用

```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
    aws-region: ap-northeast-1
```

**重要**:
- `permissions` で `id-token: write` を必ず設定
- `AWS_ACCESS_KEY_ID` や `AWS_SECRET_ACCESS_KEY` は不要

---

### パラメーターフィルタリング実装

#### 課題

全スタック共通のパラメーターファイル（`parameters/dev.json`）をそのまま渡すと、不要なパラメーターでエラー:

```
Parameters: [VendorApiDesiredCount, VendorApiTaskCpu, ...] do not exist in the template
```

#### 解決策

jq + `aws cloudformation get-template-summary` で必要なパラメーターのみ抽出:

```bash
TEMPLATE_FILE="stacks/01-network/stack.yaml"
PARAMETERS_FILE="parameters/dev.json"

# 1. テンプレートが要求するパラメーターを取得
REQUIRED_PARAMS=$(aws cloudformation get-template-summary \
  --template-body file://$TEMPLATE_FILE \
  --query 'Parameters[*].ParameterKey' \
  --output json)

# 2. パラメーターファイルからフィルタリング
FILTERED_PARAMS=$(jq --argjson required "$REQUIRED_PARAMS" '
  [ .[] | select(.ParameterKey as $k | $required | index($k)) ]
' $PARAMETERS_FILE)

# 3. フィルタリングしたパラメーターをファイルに保存
echo "$FILTERED_PARAMS" > /tmp/filtered-params.json

# 4. Change Set作成
aws cloudformation create-change-set \
  --stack-name my-stack \
  --change-set-name my-changeset \
  --template-body file://$TEMPLATE_FILE \
  --parameters file:///tmp/filtered-params.json \
  --capabilities CAPABILITY_NAMED_IAM
```

**検証結果**: ✅ 正常動作確認済み

---

### Change Set作成（preview ジョブ）

```yaml
preview:
  if: github.event_name == 'pull_request'
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4

    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
        aws-region: ap-northeast-1

    - name: Create Change Sets
      id: changeset
      run: |
        cd infra/cloudformation/service

        STACKS=("01-network" "02-database" "03-compute" "04-auth" "05-storage" "06-monitoring")
        CHANGESET_NAME="pr-${{ github.event.pull_request.number }}-$(date +%Y%m%d-%H%M%S)"
        SUMMARY=""

        for stack in "${STACKS[@]}"; do
          echo "=== Creating Change Set: $stack ==="

          STACK_NAME="facilities-dev-$stack"
          TEMPLATE_FILE="stacks/$stack/stack.yaml"
          PARAMETERS_FILE="parameters/dev.json"

          # スタックの存在確認
          if aws cloudformation describe-stacks --stack-name $STACK_NAME &>/dev/null; then
            CHANGESET_TYPE="UPDATE"
          else
            CHANGESET_TYPE="CREATE"
          fi

          # パラメーターフィルタリング
          REQUIRED_PARAMS=$(aws cloudformation get-template-summary \
            --template-body file://$TEMPLATE_FILE \
            --query 'Parameters[*].ParameterKey' \
            --output json)

          FILTERED_PARAMS=$(jq --argjson required "$REQUIRED_PARAMS" '
            [ .[] | select(.ParameterKey as $k | $required | index($k)) ]
          ' $PARAMETERS_FILE)

          echo "$FILTERED_PARAMS" > /tmp/filtered-params-$stack.json

          # Change Set 作成
          aws cloudformation create-change-set \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters file:///tmp/filtered-params-$stack.json \
            --capabilities CAPABILITY_NAMED_IAM \
            --change-set-type $CHANGESET_TYPE \
            --description "PR #${{ github.event.pull_request.number }}: ${{ github.event.pull_request.title }}" \
            || echo "Failed to create change set for $stack"

          # Change Set 完了待ち
          aws cloudformation wait change-set-create-complete \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            || true

          # 変更内容取得
          CHANGES=$(aws cloudformation describe-change-set \
            --stack-name $STACK_NAME \
            --change-set-name $CHANGESET_NAME \
            --query 'Changes[*].[ResourceChange.Action,ResourceChange.LogicalResourceId,ResourceChange.ResourceType]' \
            --output text)

          if [ -z "$CHANGES" ]; then
            SUMMARY="$SUMMARY\n**$stack**: ⚠️ No changes"
          else
            SUMMARY="$SUMMARY\n**$stack**: ✅ Changes detected\n\`\`\`\n$CHANGES\n\`\`\`"
          fi

          echo ""
        done

        # サマリーをファイルに保存
        echo -e "$SUMMARY" > /tmp/changeset-summary.txt

    - name: Comment PR with Change Set Summary
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const summary = fs.readFileSync('/tmp/changeset-summary.txt', 'utf8');

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `### CloudFormation Change Preview\n\n${summary}\n\n---\n**Change Set Name**: \`pr-${{ github.event.pull_request.number }}-*\`\n**Environment**: dev\n\n⚠️ These Change Sets are **NOT executed**. They will be executed after merge.`
          });
```

---

### Change Set実行（deploy ジョブ）

```yaml
deploy:
  if: github.event_name == 'push'
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4

    - name: Configure AWS Credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
        aws-region: ap-northeast-1

    - name: Deploy All Stacks
      run: |
        cd infra/cloudformation/service

        STACKS=("01-network" "02-database" "03-compute" "04-auth" "05-storage" "06-monitoring")

        for stack in "${STACKS[@]}"; do
          echo ""
          echo "===================================="
          echo "Deploying: $stack"
          echo "===================================="

          ./scripts/deploy.sh dev $stack || {
            echo "❌ Failed to deploy $stack"
            exit 1
          }
        done

        echo ""
        echo "===================================="
        echo "✅ All stacks deployed successfully"
        echo "===================================="
```

**重要**: `deploy.sh` スクリプト内でパラメーターフィルタリングを実施。

---

### Branch Protection Rules設定

#### 手動設定（GitHub UI）

1. リポジトリ → Settings → Branches
2. Add rule
3. Branch name pattern: `main`
4. 設定:
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Require status checks to pass before merging
     - Status checks: `preview`

#### 自動設定（gh CLI）

```bash
gh api repos/your-org/your-repo/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=preview \
  --field required_pull_request_reviews[required_approving_review_count]=1
```

**検証済み**: [Sample-AWS-SubAgent](https://github.com/k-tanaka-522/Sample-AWS-SubAgent) で設定完了

---

## ディレクトリ構造

### CloudFormation プロジェクト

```
infra/cloudformation/
├── service/                         # Service Account スタック
│   ├── stacks/                      # ライフサイクル別スタック定義
│   │   ├── 01-network/
│   │   │   └── stack.yaml
│   │   ├── 02-database/
│   │   │   └── stack.yaml
│   │   └── ...
│   ├── templates/                   # 再利用可能なネストスタック
│   │   ├── network/
│   │   │   ├── vpc.yaml
│   │   │   ├── subnets.yaml
│   │   │   └── ...
│   │   └── ...
│   ├── parameters/                  # 環境別パラメーター
│   │   ├── dev.json
│   │   ├── stg.json
│   │   └── prd.json
│   └── scripts/
│       ├── deploy.sh                # 個別スタックデプロイ（パラメーターフィルタリング実装）
│       ├── deploy-all.sh            # 全スタック一括デプロイ
│       └── destroy-all.sh           # 全スタック削除
├── shared/                          # Shared Account スタック
│   └── (同様の構造)
└── ...

.github/
└── workflows/
    └── cloudformation-deploy.yml    # CI/CD ワークフロー

scripts/
└── setup-github-oidc.sh             # OIDC自動セットアップ
```

**参考**: [CloudFormation 標準](45_cloudformation.md)

---

## IAM権限

### 必要な権限

GitHub Actions の IAM Role には、以下の権限が必要:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "ec2:*",
        "ecs:*",
        "rds:*",
        "elasticloadbalancing:*",
        "cognito-idp:*",
        "logs:*",
        "cloudwatch:*",
        "sns:*",
        "iam:*",
        "kms:*",
        "secretsmanager:*",
        "cloudfront:*",
        "ssm:*"           // ← 重要: Parameter Store アクセスに必要
      ],
      "Resource": "*"
    }
  ]
}
```

**注意**:
- `ssm:*` は、Change Set作成時に Parameter Store を参照する場合に必要
- 検証時、`ssm:GetParameters` 権限不足でエラーが発生したため追加

**本番運用時**:
- `*` は避け、最小権限の原則に従う
- リソース単位で制限（`Resource: ["arn:aws:s3:::my-bucket/*", ...]`）

---

## トラブルシューティング

### 1. SSM権限不足エラー

**エラー**:
```
User: arn:aws:sts::897167645238:assumed-role/GitHubActionsDeployRole/GitHubActions
is not authorized to perform: ssm:GetParameters
```

**解決策**:
IAM Policy に `ssm:*` を追加。

---

### 2. パラメーター不足エラー

**エラー**:
```
Parameters: [VendorApiDesiredCount, VendorApiTaskCpu, ...] do not exist in the template
```

**解決策**:
パラメーターフィルタリングを実装（jq + `get-template-summary`）。

---

### 3. Change Set作成失敗

**エラー**:
```
No updates are to be performed.
```

**原因**:
- テンプレートに変更がない
- パラメーターに変更がない

**対応**:
- Change Set作成は失敗するが、正常動作（スキップ）
- `|| true` で継続

---

## セキュリティベストプラクティス

### 1. OIDC認証

- ✅ Access Key/Secret Key を使用しない
- ✅ 一時的な認証情報のみ
- ✅ リポジトリ単位で権限制御

### 2. Branch Protection

- ✅ 承認必須（1人以上）
- ✅ `preview` ジョブ成功必須
- ✅ `main` への直接プッシュ禁止

### 3. 監査ログ

- ✅ CloudTrail で全操作記録
- ✅ GitHub Actions ログを保存
- ✅ Change Set履歴を管理

### 4. シークレット管理

- ✅ Secrets Manager でDB認証情報管理
- ✅ Parameter Store で設定値管理
- ✅ GitHub Secrets で Role ARN 管理

---

## 参考リンク

- [検証完了レポート（Sample-AWS-SubAgent）](../../../../../../sampleAWS-subagent/docs/90_運用手順/00_検証完了レポート.md)
- [CICD設計（Sample-AWS-SubAgent）](../../../../../../sampleAWS-subagent/docs/90_運用手順/01_CICD設計.md)
- [CloudFormation 標準](45_cloudformation.md)
- [AWS公式: OIDC認証](https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub Actions公式: AWS認証](https://github.com/aws-actions/configure-aws-credentials)

---

**作成日**: 2025-10-26
**最終更新**: 2025-10-26
**検証プロジェクト**: [Sample-AWS-SubAgent](https://github.com/k-tanaka-522/Sample-AWS-SubAgent)
