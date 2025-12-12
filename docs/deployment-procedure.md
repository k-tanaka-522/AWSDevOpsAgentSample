# X-Ray Watch POC デプロイ手順書

**プロジェクト**: X-Ray Watch POC
**バージョン**: 1.0.0
**最終更新**: 2025-12-12
**作成者**: PM (Claude Code)

---

## 目次

1. [前提条件](#前提条件)
2. [概要](#概要)
3. [デプロイ手順](#デプロイ手順)
   - [Step 1: RDSデータベース初期化](#step-1-rdsデータベース初期化)
   - [Step 2: CloudFormationスタック更新](#step-2-cloudformationスタック更新)
   - [Step 3: 動作確認](#step-3-動作確認)
4. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必須ツール

- [x] **AWS CLI**: バージョン2.x以上、認証情報設定済み
- [x] **psql**: PostgreSQL クライアントツール（またはAWS Systems Manager Session Manager）
- [x] **curl**: API疎通確認用

### AWS リソース情報

| リソース | 値 |
|---------|-----|
| リージョン | ap-northeast-1 |
| RDSエンドポイント | `xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com:5432` |
| DB名 | postgres |
| Secrets Manager ARN | `arn:aws:secretsmanager:ap-northeast-1:897167645238:secret:xray-poc-database/db/password-dfJNaW` |
| ALB DNS | `xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com` |
| ECR リポジトリ | `897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app` |

---

## 概要

### デプロイの背景

これまでのCloudFormation更新が失敗していた根本原因:

1. **RDSデータベースが未初期化** → tasksテーブルが存在しない
2. **FastAPIアプリ起動時にDB接続エラー** → 起動失敗
3. **ALBヘルスチェック失敗** → ECSサービス更新タイムアウト

### 正しいデプロイ順序

```
1. RDSデータベース初期化（init.sql実行）
   ↓
2. CloudFormationスタック更新（Change Set使用）
   ↓
3. 動作確認（ヘルスチェック、API疎通、X-Rayトレース）
```

**重要**: Step 1を実施せずにCloudFormation更新を実行すると、再度タイムアウトエラーが発生します。

---

## デプロイ手順

### Step 1: RDSデータベース初期化

**所要時間**: 5分
**目的**: tasksテーブルを作成し、アプリ起動時のDB接続エラーを防止

#### 1.1 Secrets Managerからパスワード取得

```bash
# パスワードを取得（JSON形式で出力される）
aws secretsmanager get-secret-value \
  --secret-id arn:aws:secretsmanager:ap-northeast-1:897167645238:secret:xray-poc-database/db/password-dfJNaW \
  --region ap-northeast-1 \
  --query SecretString \
  --output text
```

**出力例**:
```json
{"username":"postgres","password":"r6wDM7nYOPyWBCkax0rRa4sQ4U4HXelJ"}
```

パスワード: `r6wDM7nYOPyWBCkax0rRa4sQ4U4HXelJ`（上記JSONから取得）

#### 1.2 RDSに接続

**方法A: psql（ローカルから接続）**

```bash
# セキュリティグループでローカルIPからの接続を許可してから実行
psql -h xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com \
     -U postgres \
     -d postgres \
     -p 5432
```

**方法B: AWS Systems Manager Session Manager（推奨）**

EC2にpsqlクライアントをインストールしてから接続:

```bash
# EC2にSession Managerで接続
aws ssm start-session --target <EC2インスタンスID>

# EC2内でpsqlインストール（Amazon Linux 2の場合）
sudo yum install -y postgresql15

# RDSに接続
psql -h xray-poc-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com \
     -U postgres \
     -d postgres \
     -p 5432
```

#### 1.3 init.sqlを実行

RDSに接続後、以下のSQLを実行:

```sql
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
```

**期待される出力**:
```
 task_count
------------
          4
(1 row)
```

#### 1.4 データベース初期化完了の確認

```sql
-- テーブル一覧を確認
\dt

-- tasksテーブルのスキーマを確認
\d tasks

-- データを確認
SELECT * FROM tasks;
```

**チェックポイント**:
- [x] tasksテーブルが存在する
- [x] インデックスが作成されている（idx_tasks_status, idx_tasks_created_at）
- [x] サンプルデータが4件挿入されている

---

### Step 2: CloudFormationスタック更新

**所要時間**: 5～10分（ECSサービス更新含む）
**目的**: 最新のFastAPIアプリをデプロイ

#### 2.1 CloudFormation Change Set 作成（dry-run）

```bash
cd c:\dev2\AWSDevOpsAgentSample\infra\cloudformation

# Change Set作成スクリプトを実行
./scripts/create-changeset.sh xray-poc-compute
```

**スクリプト内部で実行されるコマンド**:
```bash
aws cloudformation create-change-set \
  --stack-name xray-poc-compute \
  --change-set-name deploy-$(date +%Y%m%d-%H%M%S) \
  --template-body file://stacks/03-compute.yaml \
  --parameters \
    ParameterKey=Environment,UsePreviousValue=true \
    ParameterKey=BaseStackName,UsePreviousValue=true \
    ParameterKey=SecurityStackName,UsePreviousValue=true \
    ParameterKey=DatabaseStackName,UsePreviousValue=true \
    ParameterKey=ContainerImage,ParameterValue=897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1
```

**期待される出力**:
```
Change Set 'deploy-20251212-143000' created successfully.
Change Set ARN: arn:aws:cloudformation:ap-northeast-1:897167645238:changeSet/deploy-20251212-143000/...
```

#### 2.2 Change Set 確認（差分レビュー）

**重要**: 本番環境への影響を確認するため、必ずこのステップを実施してください。

```bash
# Change Set詳細を表示
./scripts/describe-changeset.sh xray-poc-compute deploy-20251212-143000
```

**期待される差分**:
```
Changes:
- EcsTaskDefinition: Modify (ContainerImage, DATABASE_URL)
- EcsService: Modify (TaskDefinition)

ResourceChange:
  Action: Modify
  LogicalResourceId: EcsTaskDefinition
  PhysicalResourceId: arn:aws:ecs:ap-northeast-1:897167645238:task-definition/xray-poc-compute-task:3
  ResourceType: AWS::ECS::TaskDefinition
  Replacement: True
  Scope: Properties
  Details:
    - Target: ContainerDefinitions[0].Image
      Evaluation: Static
      ChangeSource: DirectModification
```

**チェックポイント**:
- [x] EcsTaskDefinitionが更新される（ContainerImageの変更）
- [x] EcsServiceが更新される（TaskDefinitionの参照）
- [x] 削除されるリソースがない（Action: Delete がない）
- [x] 影響範囲が想定通り

#### 2.3 Change Set 実行（本番適用）

**注意**: 差分レビューで問題がないことを確認してから実行してください。

```bash
# Change Set実行
./scripts/execute-changeset.sh xray-poc-compute deploy-20251212-143000
```

**期待される出力**:
```
Executing Change Set 'deploy-20251212-143000'...
Change Set execution initiated.

Waiting for stack update to complete...
```

#### 2.4 スタック更新完了待機

```bash
# スタック更新完了を待機（最大10分）
aws cloudformation wait stack-update-complete \
  --stack-name xray-poc-compute \
  --region ap-northeast-1
```

**期待される所要時間**: 5～10分

**進捗確認（別ターミナル）**:
```bash
# ECSサービスのイベントを確認
aws ecs describe-services \
  --cluster xray-poc-compute-cluster \
  --services xray-poc-compute-service \
  --region ap-northeast-1 \
  --query 'services[0].events[0:5].[createdAt,message]' \
  --output table
```

**正常な更新プロセス**:
```
1. TaskDefinition更新
2. ECSサービスがローリングアップデート開始
3. 新しいタスクが起動
4. ALBヘルスチェック成功（/health エンドポイント）
5. 古いタスクがGraceful Shutdown
6. デプロイ完了
```

---

### Step 3: 動作確認

**所要時間**: 5分
**目的**: アプリが正常に動作し、X-Rayトレースが記録されることを確認

#### 3.1 ヘルスチェック

```bash
# ALB経由でヘルスチェック
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/health
```

**期待される出力**:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "production",
  "version": "1.0.0"
}
```

**チェックポイント**:
- [x] ステータスが "healthy"
- [x] データベース接続が "connected"

#### 3.2 API疎通確認

```bash
# タスク一覧取得
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks
```

**期待される出力**:
```json
[
  {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "title": "X-Ray検証タスク1",
    "description": "AWS X-Rayの分散トレーシング検証",
    "status": "in_progress",
    "created_at": "2025-12-12T05:00:00Z",
    "updated_at": "2025-12-12T05:00:00Z"
  },
  ...
]
```

#### 3.3 障害シミュレーションエンドポイント（X-Ray検証用）

```bash
# DB遅延シミュレーション（3秒遅延）
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-db

# ロジック遅延シミュレーション（5秒遅延）
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-logic

# 外部API遅延シミュレーション（2秒遅延）
curl http://xray-poc-compute-alb-346099642.ap-northeast-1.elb.amazonaws.com/tasks/slow-external
```

**目的**: X-Rayコンソールでボトルネックが可視化されることを確認

#### 3.4 X-Rayトレース確認

1. **AWS コンソール** → **X-Ray** → **Service Map**
2. 以下のサービスマップが表示されることを確認:
   ```
   Client → ALB → ECS (FastAPI) → RDS (PostgreSQL)
                               → External API (httpbin.org)
   ```
3. **Traces** タブで個別トレースを確認:
   - DB遅延シミュレーション: PostgreSQL subsegmentが3秒
   - ロジック遅延シミュレーション: Application Logic subsegmentが5秒
   - 外部API遅延シミュレーション: External API subsegmentが2秒

**チェックポイント**:
- [x] Service Mapに全サービスが表示される
- [x] トレースデータが記録されている
- [x] 遅延箇所が可視化されている（赤くハイライト）

---

## トラブルシューティング

### 問題1: ECSサービス更新がタイムアウトする

**症状**:
```
Waiter StackUpdateComplete failed: Max attempts exceeded
```

**原因**:
- ALBヘルスチェックが失敗している
- アプリケーションが起動していない

**診断手順**:

```bash
# 1. ECSタスクのステータス確認
aws ecs list-tasks \
  --cluster xray-poc-compute-cluster \
  --service-name xray-poc-compute-service \
  --region ap-northeast-1

# 2. タスクの詳細確認
aws ecs describe-tasks \
  --cluster xray-poc-compute-cluster \
  --tasks <task-arn> \
  --region ap-northeast-1 \
  --query 'tasks[0].containers[*].[name,lastStatus,reason]' \
  --output table

# 3. CloudWatchログ確認
aws logs tail /ecs/xray-poc-compute --follow --region ap-northeast-1
```

**よくあるエラーと対処法**:

| エラーメッセージ | 原因 | 対処法 |
|----------------|------|--------|
| `CannotPullContainerError` | ECRイメージが存在しない | ECRリポジトリにイメージをプッシュ |
| `relation "tasks" does not exist` | RDSが未初期化 | **Step 1: RDSデータベース初期化**を実施 |
| `could not connect to server` | DATABASE_URLが不正 | 03-compute.yamlのDATABASE_URLを確認 |
| `HealthCheckGracePeriodSeconds exceeded` | アプリ起動が遅い | HealthCheckGracePeriodSecondsを120に増加 |

---

### 問題2: ヘルスチェックが失敗する

**症状**:
```json
{
  "status": "unhealthy",
  "database": "disconnected"
}
```

**原因**:
- DATABASE_URLが間違っている
- RDSセキュリティグループでECSからの接続が許可されていない
- RDSが起動していない

**診断手順**:

```bash
# 1. DATABASE_URL確認（ECSタスク定義）
aws ecs describe-task-definition \
  --task-definition xray-poc-compute-task \
  --region ap-northeast-1 \
  --query 'taskDefinition.containerDefinitions[0].environment' \
  --output table

# 2. RDSステータス確認
aws rds describe-db-instances \
  --region ap-northeast-1 \
  --query 'DBInstances[?DBInstanceIdentifier==`xray-poc-database-rds`].[DBInstanceStatus,Endpoint.Address]' \
  --output table

# 3. セキュリティグループ確認
aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=xray-poc-security-RdsSecurityGroup*" \
  --region ap-northeast-1 \
  --query 'SecurityGroups[0].IpPermissions' \
  --output table
```

**対処法**:
1. DATABASE_URLが正しいことを確認
2. RDSセキュリティグループのインバウンドルールでECSセキュリティグループからの接続を許可
3. RDSが "available" ステータスであることを確認

---

### 問題3: X-Rayトレースが記録されない

**症状**:
- X-Ray Service Mapにデータが表示されない
- Tracesが空

**原因**:
- X-Ray Daemonコンテナが起動していない
- IAMロールにX-Ray権限がない
- X-Ray Middleware設定が不正

**診断手順**:

```bash
# 1. X-Ray Daemonコンテナのログ確認
aws logs tail /ecs/xray-poc-compute --follow --filter-pattern "xray-daemon" --region ap-northeast-1

# 2. ECSタスクロールのIAMポリシー確認
aws iam get-role \
  --role-name xray-poc-security-EcsTaskRole-* \
  --region ap-northeast-1 \
  --query 'Role.Arn'

aws iam list-attached-role-policies \
  --role-name xray-poc-security-EcsTaskRole-* \
  --region ap-northeast-1

# 3. X-Ray Daemon接続確認（アプリログ）
aws logs tail /ecs/xray-poc-compute --follow --filter-pattern "X-Ray" --region ap-northeast-1
```

**期待されるログ（正常時）**:
```
[xray-daemon] Successfully sent batch of 1 segments
[app] X-Ray middleware initialized: localhost:2000
```

**対処法**:
1. X-Ray Daemonコンテナが "RUNNING" ステータスであることを確認
2. ECSタスクロールに `AWSXRayDaemonWriteAccess` ポリシーがアタッチされていることを確認
3. アプリ環境変数 `AWS_XRAY_DAEMON_ADDRESS=localhost:2000` が設定されていることを確認

---

### 問題4: ロールバックが必要な場合

**状況**: デプロイ後に重大な問題が発覚し、前のバージョンに戻したい

**手順**:

```bash
# 1. 前回のTaskDefinitionリビジョンを確認
aws ecs list-task-definitions \
  --family-prefix xray-poc-compute-task \
  --region ap-northeast-1 \
  --query 'taskDefinitionArns[-3:]' \
  --output table

# 2. ロールバック用Change Set作成
cd c:\dev2\AWSDevOpsAgentSample\infra\cloudformation
./scripts/rollback.sh xray-poc-compute <previous-task-definition-arn>
```

**スクリプト内部で実行されるコマンド**:
```bash
aws cloudformation create-change-set \
  --stack-name xray-poc-compute \
  --change-set-name rollback-$(date +%Y%m%d-%H%M%S) \
  --template-body file://stacks/03-compute.yaml \
  --parameters \
    ParameterKey=Environment,UsePreviousValue=true \
    ParameterKey=ContainerImage,ParameterValue=<previous-image-tag> \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1

# Change Set確認後、実行
aws cloudformation execute-change-set \
  --change-set-name rollback-20251212-150000 \
  --stack-name xray-poc-compute \
  --region ap-northeast-1
```

**注意**: ロールバックもChange Setを使用するため、dry-run（describe-changeset）を実施してから実行してください。

---

## 付録: Change Setスクリプト詳細

### create-changeset.sh

```bash
#!/bin/bash
# Change Set作成スクリプト

STACK_NAME=$1
CHANGE_SET_NAME="deploy-$(date +%Y%m%d-%H%M%S)"

aws cloudformation create-change-set \
  --stack-name $STACK_NAME \
  --change-set-name $CHANGE_SET_NAME \
  --template-body file://stacks/03-compute.yaml \
  --parameters \
    ParameterKey=Environment,UsePreviousValue=true \
    ParameterKey=ContainerImage,ParameterValue=897167645238.dkr.ecr.ap-northeast-1.amazonaws.com/xray-poc-compute-app:latest \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1

echo "Change Set '$CHANGE_SET_NAME' created. Use describe-changeset.sh to review."
```

### describe-changeset.sh

```bash
#!/bin/bash
# Change Set詳細表示（dry-run）

STACK_NAME=$1
CHANGE_SET_NAME=$2

aws cloudformation describe-change-set \
  --stack-name $STACK_NAME \
  --change-set-name $CHANGE_SET_NAME \
  --region ap-northeast-1 \
  --query 'Changes[*].[ResourceChange.Action,ResourceChange.LogicalResourceId,ResourceChange.ResourceType]' \
  --output table
```

### execute-changeset.sh

```bash
#!/bin/bash
# Change Set実行（本番適用）

STACK_NAME=$1
CHANGE_SET_NAME=$2

read -p "Execute Change Set '$CHANGE_SET_NAME' on stack '$STACK_NAME'? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Aborted."
  exit 1
fi

aws cloudformation execute-change-set \
  --change-set-name $CHANGE_SET_NAME \
  --stack-name $STACK_NAME \
  --region ap-northeast-1

echo "Change Set execution initiated. Monitor progress with: aws cloudformation describe-stack-events --stack-name $STACK_NAME"
```

### rollback.sh

```bash
#!/bin/bash
# ロールバック用Change Set作成

STACK_NAME=$1
PREVIOUS_IMAGE=$2
CHANGE_SET_NAME="rollback-$(date +%Y%m%d-%H%M%S)"

aws cloudformation create-change-set \
  --stack-name $STACK_NAME \
  --change-set-name $CHANGE_SET_NAME \
  --template-body file://stacks/03-compute.yaml \
  --parameters \
    ParameterKey=Environment,UsePreviousValue=true \
    ParameterKey=ContainerImage,ParameterValue=$PREVIOUS_IMAGE \
  --capabilities CAPABILITY_IAM \
  --region ap-northeast-1

echo "Rollback Change Set '$CHANGE_SET_NAME' created. Review with describe-changeset.sh before executing."
```

---

## まとめ

このデプロイ手順書に従うことで、以下が担保されます:

1. **安全性**: Change Setによるdry-run必須
2. **信頼性**: RDS初期化を事前実施し、ヘルスチェック失敗を防止
3. **可観測性**: X-Rayトレース確認手順を明記
4. **復旧性**: ロールバック手順を記載

**重要な注意事項**:
- Step 1（RDS初期化）を省略しないこと
- Change Set実行前に必ずdescribe-changesetで差分確認すること
- 本番環境への直接デプロイ（`aws cloudformation deploy`）は禁止

---

**作成日**: 2025-12-12
**レビュー状態**: Draft
**次回レビュー日**: 初回デプロイ完了後
