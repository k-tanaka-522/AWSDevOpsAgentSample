# AWS CloudFormation 規約

## 基本方針

- **Change Sets必須**（dry-run）
- **Well-Architected Framework準拠**
- **設計で判断**（技術標準は推奨であり、プロジェクト要件に応じて調整可能）

---

## 📋 設計書とテンプレートの区別

### 重要な区別

| 成果物 | フェーズ | ファイル構成 | 目的 |
|-------|--------|-----------|------|
| **基本設計書** | 設計フェーズ | 常に複数ファイルに分割 | レビューしやすさ、並行作業 |
| **CloudFormation テンプレート** | 実装フェーズ | ファイル分割3原則に基づく | メンテナンス性、変更リスク最小化 |

### 基本設計書のファイル分割（ベストプラクティス）

基本設計書は、規模に関わらず以下の構成で複数ファイルに分割してください：

```
docs/03_基本設計/
├── INDEX.md                          # 目次・全体像・レビュー状況
├── 01_システムアーキテクチャ.md         # 全体構成図、システム構成要素
├── 02_ネットワーク設計.md              # VPC、サブネット、ルーティング
├── 03_セキュリティ設計.md              # Security Groups、WAF、認証、暗号化
├── 04_監査・コンプライアンス設計.md      # ログ保管、証跡管理、法令準拠
├── 05_データベース設計.md              # RDS構成、バックアップ戦略
├── 06_コンピュート設計.md              # ECS、ALB、AutoScaling
├── 07_フロントエンド設計.md            # CloudFront、S3
├── 08_監視・アラート設計.md            # CloudWatch、SNS、通知
├── 09_CI_CD設計.md                    # パイプライン、デプロイ戦略
├── 10_CloudFormation構成方針.md       # ⭐ ファイル分割3原則、ディレクトリ構造
├── 11_非機能要件実現方針.md            # 性能、可用性
├── 12_災害対策・BCP.md                # DR、バックアップ
└── 13_移行計画.md                     # スケジュール、データ移行
```

**重要**: `10_CloudFormation構成方針.md` には、実装フェーズで使用する**ファイル分割3原則**と**ディレクトリ構造**を必ず記載してください。

---

## ファイル分割の3原則（CloudFormation テンプレート用）

### なぜファイルを分割するのか？

**目的:**
1. **メンテナンス性**: 変更箇所がすぐわかる
2. **変更リスクの最小化**: 影響範囲を限定
3. **並行作業**: チームで同時に異なるリソースを編集可能
4. **可読性**: ファイル名で何があるかすぐわかる

### 3原則

CloudFormation のファイル分割は、以下の3原則に基づいて判断します：

#### 原則1: AWS コンソールの分け方（基本）

**AWS コンソールで別メニュー → 別ファイル**

- ✅ VPC と Subnets → 別ファイル（別メニュー）
- ✅ VPC と Internet Gateway → 同じファイル（VPC作成時に一緒に作る、密結合）
- ✅ ALB と Target Group と Listener → 同じファイル（ALB配下で一緒に操作）
- ✅ ECS Cluster と ECS Service → 別ファイル（別メニュー）

**理由**: AWS コンソールの構造は、AWS が推奨するリソースの論理的なまとまりを反映しています。

#### 原則2: ライフサイクル（変更頻度）

**初回のみ作成 vs 頻繁に変更 → 分ける**

- ✅ ECS Cluster（変更少） vs Task Definition（変更多） → 別ファイル
- ✅ VPC（初回のみ） vs Security Groups（継続的に追加） → 別ファイル
- ✅ Route53 Hosted Zone（初回のみ） vs Route53 Records（継続的に追加） → 別ファイル

**理由**: 変更頻度が異なるリソースを分けることで、変更リスクを最小化できます。

**AWS公式推奨**: ライフサイクル・オーナーシップで分割

| 更新頻度 | リソース例 | 分離推奨 |
|---------|----------|--------|
| 年単位 | VPC, Subnet, RouteTable | network/ |
| 月単位 | RDS, DynamoDB, S3 | database/ |
| 週単位 | ECS Service, ALB, Auto Scaling | compute/ |
| 日単位 | Task Definition | compute/ecs-task-*.yaml |

#### 原則3: 設定数（増減の可能性）

**1個で固定 vs 継続的に増える → 分ける**

- ✅ VPC（1個） + IGW（1個） → 同じファイルOK
- ✅ Security Groups（激増） → ディレクトリで分割
- ✅ CloudWatch Alarms（激増） → サービス別にファイル分割

**増えやすいリソースの例**:
- Security Groups → `security-groups/alb-sg.yaml`, `security-groups/ecs-sg.yaml`
- CloudWatch Alarms → `cloudwatch-alarms-ecs.yaml`, `cloudwatch-alarms-rds.yaml`
- Route53 Records → `route53-records-api.yaml`, `route53-records-web.yaml`

### 判断フロー

```
1. AWS コンソールで別メニュー？
   ├─ Yes → 分割候補
   └─ No → 同じファイル候補

2. ライフサイクルが異なる？
   ├─ Yes → 分割推奨
   └─ No → 次へ

3. 設定が継続的に増える？
   ├─ Yes → 分割推奨（ディレクトリ化も検討）
   └─ No → 同じファイルでOK
```

### 判断例

| リソース | コンソール | ライフサイクル | 設定数 | 判定 |
|---------|-----------|--------------|--------|------|
| VPC + IGW | 密結合 | 初回のみ | 1個 | 同じファイル |
| Subnets | 別メニュー | たまに追加 | 4個→増える | 別ファイル |
| Security Groups | 別メニュー | 継続的に追加 | 3個→激増 | ディレクトリ |
| ECS Cluster | 別メニュー | 初回のみ | 1個 | 別ファイル |
| Task Definition | 同じメニュー | 頻繁に変更 | 増える | サービス別 |
| ALB + TG + Listener | ALB配下 | たまに変更 | 1個 | 同じファイル |

### クロススタック参照（Export/Import）

**network-stack** (Exportする側)
```yaml
Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub ${ProjectName}-${Environment}-VpcId

  PrivateSubnetIds:
    Value: !Join [",", [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub ${ProjectName}-${Environment}-PrivateSubnetIds
```

**compute-stack** (Importする側)
```yaml
Resources:
  ECSService:
    Type: AWS::ECS::Service
    Properties:
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Split
            - ","
            - !ImportValue
                Fn::Sub: ${ProjectName}-${Environment}-PrivateSubnetIds
```

---

## ディレクトリ構造

### 推奨構造（ライフサイクル別スタック + 再利用可能テンプレート）

```
infra/cloudformation/
├── README.md                        # 全体インデックス、3原則の説明、よくある変更の対応表
├── stacks/                          # ライフサイクル別スタック定義（デプロイ単位）⭐
│   ├── 01-network/                  # 年単位（初回のみ、慎重に変更）
│   │   ├── main.yaml                # 親スタック（templates/network/*.yaml を参照）
│   │   └── README.md                # なぜこのスタックに分けたか、デプロイ戦略
│   ├── 02-database/                 # 月単位（たまに変更）
│   │   ├── main.yaml                # 親スタック（templates/database/*.yaml を参照）
│   │   └── README.md
│   ├── 03-compute-base/             # 月単位（ECS Cluster, ALB等）
│   │   ├── main.yaml                # 親スタック（templates/compute/cluster.yaml等を参照）
│   │   └── README.md
│   └── 04-compute-app/              # 週単位（Task Definition, Service、頻繁に変更）
│       ├── main.yaml                # 親スタック（templates/compute/ecs-task-*.yaml等を参照）
│       └── README.md
├── templates/                       # 再利用可能なネストスタック（実体）⭐
│   ├── network/
│   │   ├── vpc-and-igw.yaml         # VPC+IGW（密結合、初回のみ、1個）
│   │   ├── subnets.yaml             # Subnets（別メニュー、たまに追加、増える）
│   │   ├── route-tables.yaml        # Route Tables（別メニュー、たまに変更）
│   │   ├── nat-gateways.yaml        # NAT GW（別メニュー、初回のみ、高額）
│   │   └── security-groups/         # ★ ディレクトリ（激増する）
│   │       ├── alb-sg.yaml
│   │       ├── ecs-sg.yaml
│   │       └── rds-sg.yaml
│   ├── database/
│   │   ├── rds-instance.yaml        # RDS（別メニュー、たまに変更、1個）
│   │   └── rds-security-group.yaml  # RDS SG（設定複雑なので分離）
│   ├── compute/
│   │   ├── ecr-repositories.yaml    # ECR（別メニュー、たまに追加、増える）
│   │   ├── ecs-cluster.yaml         # Cluster（別メニュー、初回のみ、1個）
│   │   ├── ecs-task-public-web.yaml # Task（頻繁に変更、サービス別）
│   │   ├── ecs-service-public-web.yaml # Service（たまに変更、サービス別）
│   │   ├── ecs-task-admin-api.yaml
│   │   ├── ecs-service-admin-api.yaml
│   │   └── alb.yaml                 # ALB+TG+Listener（密結合、1個）
│   └── monitoring/
│       ├── cloudwatch-log-groups.yaml   # Log Groups（別メニュー、増える）
│       ├── cloudwatch-alarms-ecs.yaml   # Alarms（激増、サービス別）
│       ├── cloudwatch-alarms-rds.yaml
│       ├── cloudwatch-alarms-alb.yaml
│       └── eventbridge-rules.yaml       # EventBridge（別メニュー、増える）
└── parameters/                      # 環境差分を集約 ⭐
    ├── dev.json
    ├── stg.json
    └── prd.json
```

### 3つのディレクトリの役割

| ディレクトリ | 役割 | 分け方 | 例 |
|------------|------|--------|---|
| **stacks/** | デプロイ単位（親スタック） | ライフサイクル（変更頻度） | 01-network（年1回）、04-compute-app（週数回） |
| **templates/** | 実装（ネストスタック） | 機能別 + 3原則 | network/vpc.yaml、compute/ecs-task.yaml |
| **parameters/** | 環境差分 | 環境別 | dev.json、stg.json、prd.json |

### stacks/ と templates/ の対応関係

**stacks/01-network/main.yaml（親スタック）:**
```yaml
Resources:
  VPCStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub https://s3.amazonaws.com/${TemplateBucket}/templates/network/vpc-and-igw.yaml
      Parameters:
        Environment: !Ref Environment
        VpcCidr: !Ref VpcCidr

  SubnetsStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub https://s3.amazonaws.com/${TemplateBucket}/templates/network/subnets.yaml
      Parameters:
        VpcId: !GetAtt VPCStack.Outputs.VpcId
```

**templates/network/vpc-and-igw.yaml（ネストスタック、再利用可能）:**
```yaml
Parameters:
  Environment:
    Type: String
  VpcCidr:
    Type: String

Resources:
  ServiceVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-${Environment}-vpc

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    # ...

Outputs:
  VpcId:
    Value: !Ref ServiceVPC
    Export:
      Name: !Sub ${ProjectName}-${Environment}-VpcId
```

### プロジェクト規模別の推奨構成

#### 小規模プロジェクト（リソース数が少ない、変更頻度が一定）

```
infra/cloudformation/
├── README.md
├── stacks/
│   └── main.yaml                    # 全リソースを1つのスタックで管理 ⭐
├── templates/                       # ネストスタックで機能分割
│   ├── network/
│   │   └── vpc-and-subnets.yaml
│   ├── compute/
│   │   └── ecs.yaml
│   └── database/
│       └── rds.yaml
└── parameters/
    ├── dev.json
    └── prd.json
```

**特徴**:
- スタックは1つ（`stacks/main.yaml`）
- ライフサイクル分割は不要（リソース数が少ない）
- templates/ で機能分割のみ（メンテナンス性確保）

#### 中〜大規模プロジェクト（リソース数が多い、変更頻度が異なる）

前述の「ライフサイクル別スタック」構成を使用。

### README.md インデックスの例

**`infra/cloudformation/README.md`**:
```markdown
# CloudFormation Templates

## 📁 構成（ライフサイクル別スタック）

### スタック構成
| スタック | 変更頻度 | デプロイ戦略 | 含まれるリソース |
|---------|--------|------------|----------------|
| 01-network | 年1回 | 手動、複数人承認 | VPC, Subnets, NAT GW, Security Groups |
| 02-database | 月1回 | 手動、1人承認 | RDS, DynamoDB |
| 03-compute-base | 月1回 | 手動、1人承認 | ECS Cluster, ALB |
| 04-compute-app | 週数回 | 自動（main マージ時） | Task Definition, ECS Service |

### テンプレート構成（templates/）
- **network/** - VPC、サブネット、セキュリティグループ（3原則ベース）
- **database/** - RDS、バックアップ設定
- **compute/** - ECS、ALB、タスク定義（サービス別）
- **monitoring/** - CloudWatch、EventBridge（サービス別）

## 🔍 よくある変更

| やりたいこと | 編集するファイル | デプロイするスタック |
|------------|----------------|-------------------|
| VPC の CIDR を変更 | `templates/network/vpc-and-igw.yaml` | 01-network |
| RDS のインスタンスクラス変更 | `parameters/prd.json` | 02-database |
| ECS のタスク定義変更 | `templates/compute/ecs-task-public-web.yaml` | 04-compute-app |
| CloudWatch アラーム追加 | `templates/monitoring/cloudwatch-alarms-ecs.yaml` | 04-compute-app |
```

### 使い方

#### ライフサイクル別スタックのデプロイ順序

```bash
# 1. Network Stack（最初、年1回程度）
./scripts/deploy.sh dev 01-network

# 2. Database Stack（月1回程度）
./scripts/deploy.sh dev 02-database

# 3. Compute Base Stack（月1回程度）
./scripts/deploy.sh dev 03-compute-base

# 4. Compute App Stack（週数回、頻繁に更新）
./scripts/deploy.sh dev 04-compute-app
```

#### 全スタック一括デプロイ

```bash
# 依存関係順に全スタックデプロイ
./scripts/deploy-all.sh dev
```

### parameters/dev.json の例（環境差分を集約）

```json
[
  {
    "ParameterKey": "Environment",
    "ParameterValue": "dev"
  },
  {
    "ParameterKey": "ProjectName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "VpcCidr",
    "ParameterValue": "10.1.0.0/16"
  },
  {
    "ParameterKey": "DBInstanceClass",
    "ParameterValue": "db.t3.micro"
  },
  {
    "ParameterKey": "ECSTaskCpu",
    "ParameterValue": "256"
  }
]
```

**すべての環境差分（dev/prod）がこのファイルに集約される**

### 複雑なプロジェクトの場合

Platform Account / Service Account など、複数のAWSアカウントを使用する場合：

```
infra/cloudformation/
├── platform/                      # Platform Account用
│   ├── stacks/
│   │   ├── network/
│   │   │   └── main.yaml
│   │   └── connectivity/
│   │       └── main.yaml         # TGW, RAM
│   ├── templates/
│   │   └── ...
│   └── parameters/
│       ├── dev.json
│       └── prod.json
│
└── service/                       # Service Account用
    ├── stacks/
    │   ├── network/
    │   ├── storage/
    │   └── compute/
    ├── templates/
    │   └── ...
    └── parameters/
        ├── dev.json
        └── prod.json
```

---

## テンプレート規約

### パラメータ必須項目

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues:
      - dev
      - stg
      - prd
    Description: Environment name

  ProjectName:
    Type: String
    Description: Project name for resource naming
```

### リソース命名規則

```yaml
Resources:
  MyAppVPC:
    Type: AWS::EC2::VPC
    Properties:
      Tags:
        - Key: Name
          Value: !Sub ${ProjectName}-${Environment}-vpc
        - Key: Environment
          Value: !Ref Environment
```

---

## デプロイ手順（Change Sets必須）

```bash
# ❌ Bad: 直接デプロイ
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name myapp-prd

# ✅ Good: Change Setsで確認
# 1. Change Set作成
aws cloudformation create-change-set \
  --stack-name myapp-prd \
  --change-set-name update-2025-10-19 \
  --template-body file://template.yaml

# 2. Change Set確認
aws cloudformation describe-change-set \
  --stack-name myapp-prd \
  --change-set-name update-2025-10-19

# 3. 承認後、実行
aws cloudformation execute-change-set \
  --stack-name myapp-prd \
  --change-set-name update-2025-10-19
```

---

## Well-Architected Framework

### 6つの柱

1. **セキュリティ**: IAM、暗号化、SecurityGroup
2. **信頼性**: Multi-AZ、バックアップ
3. **パフォーマンス効率**: Auto Scaling
4. **コスト最適化**: リソース最適化
5. **運用上の優秀性**: CloudWatch、ログ
6. **持続可能性**: リソース効率化

---

## ファイル分割の判断基準

### コメント見出しレベルで判断

**行数ではなく、コメント見出しの数で判断します。**

CloudFormation テンプレートには、見出しレベルがあります：

```yaml
# ==============================================================================
# Resources  ← 大見出し（セクション）
# ==============================================================================

# ------------------------------------------------------------------------------
# VPC  ← 中見出し（リソースの論理的なまとまり）
# ------------------------------------------------------------------------------
ServiceVPC:
  Type: AWS::EC2::VPC
  # ...

# ------------------------------------------------------------------------------
# Internet Gateway  ← 中見出し
# ------------------------------------------------------------------------------
InternetGateway:
  Type: AWS::EC2::InternetGateway
  # ...
```

**判断基準**:
- **中見出し (`# ----`) が3個以上** → 分割を検討
- 中見出し1つ = nested スタック1ファイル

### 判断フロー

```
ファイルを見る
  ↓
中見出し (`# ----`) が何個ある？
  ↓
├─ 1〜2個 → そのまま（分割不要）
├─ 3〜5個 → 分割を検討（3原則で判断）
└─ 6個以上 → 分割推奨
```

### 例外ケース

**分割しない方がいい場合**:
- 中見出しが複数あっても、密結合（必ず一緒に変更）
  - 例: VPC + IGW + VPC Attachment → 1ファイルでOK
  - 例: ALB + TargetGroup + Listener → 1ファイルでOK

**さらに細かく分割する場合**:
- 中見出し内のリソースが10個以上
  - 例: CloudWatch Alarms が20個 → サービス別に分割

### Good Example

#### ✅ 中見出し2個、密結合 → 1ファイル

```yaml
# 設計書に記載:
# 「VPC と IGW は密結合のため、1ファイルで管理。
#  推定200行だが、必ず一緒に変更するため分割しない。」

# ------------------------------------------------------------------------------
# VPC
# ------------------------------------------------------------------------------
ServiceVPC: ...

# ------------------------------------------------------------------------------
# Internet Gateway  ← VPC と密結合
# ------------------------------------------------------------------------------
InternetGateway: ...
AttachGateway: ...
```

#### ✅ 中見出し5個 → ネスト構成に分割

```yaml
# 設計書に記載:
# 「compute.yaml は中見出しが5個あり、3原則で判断した結果、
#  ネスト構成に分割:
#  - ecr-repositories.yaml（別メニュー）
#  - ecs-cluster.yaml（初回のみ）
#  - ecs-task-public-web.yaml（頻繁に変更）
#  - ecs-service-public-web.yaml（たまに変更）
#  - alb.yaml（ALB+TG+Listener、密結合）」

# 元のファイル（760行、中見出し5個）:
# ------------------------------------------------------------------------------
# ECR Repositories
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# ECS Cluster
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# ECS Task Definition
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# ECS Service
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Application Load Balancer
# ------------------------------------------------------------------------------
```

### Bad Example

#### ❌ 中見出し5個、752行で1ファイル（理由なし）

```yaml
# 設計書に記載なし
# → 実装時に「とりあえず全部入れた」
# → なぜこの構成か説明できない
# → メンテナンス時にどこを変更すればいいかわからない
```

---

## デプロイ自動化

### 必須スクリプト

**すべてのCloudFormationプロジェクトには、以下のスクリプトが必要です:**

**責務分離パターン（推奨）:**

```
infra/cloudformation/
├── scripts/
│   ├── create-changeset.sh      # Change Set作成のみ
│   ├── describe-changeset.sh    # Change Set詳細表示（dry-run）
│   ├── execute-changeset.sh     # Change Set実行のみ
│   ├── deploy.sh                # 上記3つを順番に実行（オーケストレーション）
│   ├── validate.sh              # テンプレート検証
│   ├── rollback.sh              # ロールバック
│   ├── deploy-all.sh            # 全スタック一括デプロイ（中規模以上）
│   ├── import-resources.sh      # 手動設定のリソースインポート（オプション）
│   └── save-changeset-log.sh    # Change Set監査ログ保存（オプション）
└── ...
```

**責務分離の利点:**
- ✅ CI/CDパイプラインで段階的に実行可能
- ✅ Change Set作成と実行の間に手動承認フローを挟める
- ✅ dry-run（Change Set確認のみ）が簡単
- ✅ テスト・デバッグがしやすい

### create-changeset.sh の実装例

**Change Set作成のみ（責務分離）:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set作成
# ==============================================================================
# 使い方:
#   ./scripts/create-changeset.sh dev 01-network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  echo "  Example: $0 dev 01-network"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
TEMPLATE_FILE="stacks/${STACK_TYPE}/main.yaml"
PARAMETERS_FILE="parameters/${ENVIRONMENT}.json"
CHANGE_SET_NAME="deploy-$(date +%Y%m%d-%H%M%S)"

echo "Creating Change Set: ${CHANGE_SET_NAME}"

# 1. テンプレート検証
aws cloudformation validate-template \
  --template-body file://${TEMPLATE_FILE} \
  > /dev/null

# 2. Change Set作成
aws cloudformation create-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --template-body file://${TEMPLATE_FILE} \
  --parameters file://${PARAMETERS_FILE} \
  --capabilities CAPABILITY_NAMED_IAM \
  --change-set-type $(aws cloudformation describe-stacks --stack-name ${STACK_NAME} &>/dev/null && echo "UPDATE" || echo "CREATE")

# 3. 待機
aws cloudformation wait change-set-create-complete \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}

echo "✅ Change Set created: ${CHANGE_SET_NAME}"
echo "${CHANGE_SET_NAME}" > /tmp/changeset-${STACK_NAME}.txt
```

### describe-changeset.sh の実装例

**Change Set詳細表示（dry-run）:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set詳細表示（dry-run）
# ==============================================================================
# 使い方:
#   ./scripts/describe-changeset.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
CHANGE_SET_NAME=$(cat /tmp/changeset-${STACK_NAME}.txt)

echo "===================================="
echo "Change Set Details (dry-run)"
echo "===================================="
echo "Stack:      ${STACK_NAME}"
echo "Change Set: ${CHANGE_SET_NAME}"
echo "===================================="

aws cloudformation describe-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --query 'Changes[].{Action:ResourceChange.Action,LogicalId:ResourceChange.LogicalResourceId,Type:ResourceChange.ResourceType,Replacement:ResourceChange.Replacement}' \
  --output table

echo ""
echo "ℹ️  This is a dry-run. To apply these changes, run:"
echo "   ./scripts/execute-changeset.sh ${ENVIRONMENT} ${STACK_TYPE}"
```

### execute-changeset.sh の実装例

**Change Set実行のみ:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set実行
# ==============================================================================
# 使い方:
#   ./scripts/execute-changeset.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
CHANGE_SET_NAME=$(cat /tmp/changeset-${STACK_NAME}.txt)

# 本番環境のみ承認プロンプト
if [ "$ENVIRONMENT" = "prd" ]; then
  read -p "Execute Change Set '${CHANGE_SET_NAME}' on ${STACK_NAME}? (yes/no): " CONFIRM
  if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
  fi
fi

echo "Executing Change Set: ${CHANGE_SET_NAME}"

aws cloudformation execute-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}

echo "Waiting for stack update..."
aws cloudformation wait stack-update-complete \
  --stack-name ${STACK_NAME} || aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}

echo "✅ Deployment completed: ${STACK_NAME}"
rm -f /tmp/changeset-${STACK_NAME}.txt
```

### deploy.sh の実装例（オーケストレーション）

**上記3つを順番に実行:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation デプロイ（オーケストレーション）
# ==============================================================================
# 使い方:
#   ./scripts/deploy.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

# 1. Change Set作成
./scripts/create-changeset.sh ${ENVIRONMENT} ${STACK_TYPE}

# 2. Change Set詳細表示（dry-run）
./scripts/describe-changeset.sh ${ENVIRONMENT} ${STACK_TYPE}

# 3. Change Set実行
./scripts/execute-changeset.sh ${ENVIRONMENT} ${STACK_TYPE}
```

### diff.sh の実装例（dry-run専用）

**Change Setを作成して確認のみ（実行しない）:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Diff (Change Set確認のみ)
# ==============================================================================
# 使い方:
#   ./scripts/diff.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
TEMPLATE_FILE="stacks/${STACK_TYPE}/main.yaml"
PARAMETERS_FILE="parameters/${ENVIRONMENT}.json"
CHANGE_SET_NAME="diff-$(date +%Y%m%d-%H%M%S)"

echo "Creating Change Set (dry-run)..."
aws cloudformation create-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --template-body file://${TEMPLATE_FILE} \
  --parameters file://${PARAMETERS_FILE} \
  --capabilities CAPABILITY_NAMED_IAM \
  --change-set-type $(aws cloudformation describe-stacks --stack-name ${STACK_NAME} &>/dev/null && echo "UPDATE" || echo "CREATE")

aws cloudformation wait change-set-create-complete \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}

echo "===================================="
echo "Change Set Details (dry-run)"
echo "===================================="
aws cloudformation describe-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --query 'Changes[].{Action:ResourceChange.Action,LogicalId:ResourceChange.LogicalResourceId,Type:ResourceChange.ResourceType,Replacement:ResourceChange.Replacement}' \
  --output table

echo ""
echo "ℹ️  This is a dry-run. No changes were applied."
echo "To apply these changes, run: ./scripts/deploy.sh ${ENVIRONMENT} ${STACK_TYPE}"

# Change Setを削除（dry-runなので実行しない）
aws cloudformation delete-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}
```

### validate.sh の実装例

**テンプレート検証のみ:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Template Validation
# ==============================================================================

echo "Validating CloudFormation templates..."

TEMPLATES=$(find stacks -name "*.yaml")

for TEMPLATE in $TEMPLATES; do
  echo "Checking: $TEMPLATE"
  aws cloudformation validate-template \
    --template-body file://${TEMPLATE} \
    > /dev/null
  echo "✅ $TEMPLATE"
done

echo "✅ All templates are valid"
```

### rollback.sh の実装例

**スタックのロールバック:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Rollback
# ==============================================================================
# 使い方:
#   ./scripts/rollback.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"

echo "===================================="
echo "Rolling back: ${STACK_NAME}"
echo "===================================="

read -p "Are you sure? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Rollback cancelled."
  exit 0
fi

aws cloudformation rollback-stack --stack-name ${STACK_NAME}

echo "Waiting for rollback..."
aws cloudformation wait stack-rollback-complete --stack-name ${STACK_NAME}

echo "✅ Rollback completed: ${STACK_NAME}"
```

### save-changeset-log.sh の実装例（監査ログ）

**Change Set詳細をS3に保存:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set監査ログ保存
# ==============================================================================
# 使い方:
#   ./scripts/save-changeset-log.sh dev network
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <environment> <stack-type>"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
CHANGE_SET_NAME=$(cat /tmp/changeset-${STACK_NAME}.txt 2>/dev/null || echo "latest")
LOG_BUCKET="${PROJECT_NAME}-cloudformation-logs"
LOG_KEY="changelogs/${STACK_NAME}/${CHANGE_SET_NAME}.json"

echo "Saving Change Set log to S3..."

# Change Set詳細をJSON形式で取得
aws cloudformation describe-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --output json > /tmp/changeset-log.json

# S3に保存
aws s3 cp /tmp/changeset-log.json s3://${LOG_BUCKET}/${LOG_KEY}

echo "✅ Change Set log saved: s3://${LOG_BUCKET}/${LOG_KEY}"
rm -f /tmp/changeset-log.json
```

### import-resources.sh の実装例（手動設定のインポート）

**コンソールで手動作成したリソースをIaC管理下に:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation リソースインポート
# ==============================================================================
# 使い方:
#   ./scripts/import-resources.sh dev network resources-to-import.json
# ==============================================================================

ENVIRONMENT=$1
STACK_TYPE=$2
IMPORT_FILE=$3

if [ -z "$ENVIRONMENT" ] || [ -z "$STACK_TYPE" ] || [ -z "$IMPORT_FILE" ]; then
  echo "Usage: $0 <environment> <stack-type> <import-file>"
  echo "  import-file: JSON file with resources to import"
  echo "  Example: resources-to-import.json"
  exit 1
fi

PROJECT_NAME="myapp"
STACK_NAME="${PROJECT_NAME}-${ENVIRONMENT}-${STACK_TYPE}"
TEMPLATE_FILE="stacks/${STACK_TYPE}/main.yaml"
PARAMETERS_FILE="parameters/${ENVIRONMENT}.json"
CHANGE_SET_NAME="import-$(date +%Y%m%d-%H%M%S)"

echo "===================================="
echo "Importing resources to: ${STACK_NAME}"
echo "===================================="

# Change Set作成（Import タイプ）
aws cloudformation create-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --change-set-type IMPORT \
  --resources-to-import file://${IMPORT_FILE} \
  --template-body file://${TEMPLATE_FILE} \
  --parameters file://${PARAMETERS_FILE} \
  --capabilities CAPABILITY_NAMED_IAM

echo "Waiting for Change Set creation..."
aws cloudformation wait change-set-create-complete \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}

# Change Set詳細表示
aws cloudformation describe-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --query 'Changes[].{Action:ResourceChange.Action,LogicalId:ResourceChange.LogicalResourceId,Type:ResourceChange.ResourceType}' \
  --output table

read -p "Execute this import? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Import cancelled."
  exit 0
fi

# Change Set実行
aws cloudformation execute-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME}

echo "Waiting for import..."
aws cloudformation wait stack-import-complete --stack-name ${STACK_NAME}

echo "✅ Import completed: ${STACK_NAME}"
```

**resources-to-import.json の例:**

```json
[
  {
    "ResourceType": "AWS::EC2::VPC",
    "LogicalResourceId": "ServiceVPC",
    "ResourceIdentifier": {
      "VpcId": "vpc-0123456789abcdef0"
    }
  },
  {
    "ResourceType": "AWS::EC2::Subnet",
    "LogicalResourceId": "PrivateSubnet1",
    "ResourceIdentifier": {
      "SubnetId": "subnet-0123456789abcdef0"
    }
  }
]
```

### 依存関係の順序制御（deploy-all.sh）

**複数スタックを順番にデプロイ:**

```bash
#!/bin/bash
set -euo pipefail

# ==============================================================================
# 全スタックデプロイ（ライフサイクル順、依存関係順）
# ==============================================================================

ENVIRONMENT=$1

if [ -z "$ENVIRONMENT" ]; then
  echo "Usage: $0 <environment>"
  echo "  Example: $0 dev"
  exit 1
fi

echo "Deploying all stacks in lifecycle order..."

# 1. Network Stack（初回のみ、他のスタックが依存）
./scripts/deploy.sh ${ENVIRONMENT} 01-network

# 2. Database Stack（Network Stackに依存）
./scripts/deploy.sh ${ENVIRONMENT} 02-database

# 3. Compute Base Stack（Network Stackに依存）
./scripts/deploy.sh ${ENVIRONMENT} 03-compute-base

# 4. Compute App Stack（Compute Base Stackに依存、頻繁に更新）
./scripts/deploy.sh ${ENVIRONMENT} 04-compute-app

echo "✅ All stacks deployed successfully"
```

### README.md への記載例

**`infra/cloudformation/README.md`:**

```markdown
# CloudFormation Templates

## デプロイ方法

### 前提条件
- AWS CLI設定済み (`aws configure`)
- 適切なIAMロール

### 環境別デプロイ

```bash
# dry-run（Change Set確認のみ）
./scripts/diff.sh dev 01-network

# dev環境にデプロイ（ライフサイクル順）
./scripts/deploy.sh dev 01-network
./scripts/deploy.sh dev 02-database
./scripts/deploy.sh dev 03-compute-base
./scripts/deploy.sh dev 04-compute-app

# prod環境にデプロイ（確認プロンプトあり）
./scripts/deploy.sh prod 01-network
```

### テンプレート検証

```bash
./scripts/validate.sh
```

### ロールバック

```bash
./scripts/rollback.sh dev 04-compute-app
```

### 全スタック一括デプロイ

```bash
./scripts/deploy-all.sh dev
```

## スタック依存関係（ライフサイクル順）

```
01-network (VPC, Subnets, Security Groups) ← 年1回
  ↓
02-database (RDS, DynamoDB) ← 月1回
  ↓
03-compute-base (ECS Cluster, ALB) ← 月1回
  ↓
04-compute-app (Task Definition, Service) ← 週数回
```
```

---

## CI/CDパイプライン統合

### ライフサイクル別デプロイ戦略

| スタック | 変更頻度 | トリガー | 承認 | デプロイ戦略 |
|---------|--------|---------|------|------------|
| 01-network | 年1回 | 手動のみ | 複数人 | 手動トリガー + Change Set確認 + 複数人承認 |
| 02-database | 月1回 | 手動のみ | 1人 | 手動トリガー + Change Set確認 + 1人承認 |
| 03-compute-base | 月1回 | 手動のみ | 1人 | 手動トリガー + Change Set確認 + 1人承認 |
| 04-compute-app | 週数回 | main マージ | dry-run | PR時 dry-run → main マージで自動デプロイ |

### GitHub Actions例（ライフサイクル別パターン）

#### 1. Pull Request時（全スタック dry-run）

```yaml
name: CloudFormation Dry-Run

on:
  pull_request:
    paths:
      - 'infra/cloudformation/**'

jobs:
  dry-run:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        stack: ['01-network', '02-database', '03-compute-base', '04-compute-app']
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1

      - name: Validate templates
        run: ./scripts/validate.sh

      - name: Create Change Set
        run: ./scripts/create-changeset.sh dev ${{ matrix.stack }}

      - name: Describe Change Set (dry-run)
        run: ./scripts/describe-changeset.sh dev ${{ matrix.stack }}

      - name: Save Change Set log
        run: ./scripts/save-changeset-log.sh dev ${{ matrix.stack }}
```

#### 2. main マージ時（04-compute-app のみ自動デプロイ）

```yaml
name: CloudFormation Deploy Compute App

on:
  push:
    branches:
      - main
    paths:
      - 'infra/cloudformation/templates/compute/**'
      - 'infra/cloudformation/stacks/04-compute-app/**'

jobs:
  deploy-compute-app:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1

      - name: Validate templates
        run: ./scripts/validate.sh

      - name: Deploy Compute App Stack
        run: ./scripts/deploy.sh dev 04-compute-app

      - name: Rollback on failure
        if: failure()
        run: ./scripts/rollback.sh dev 04-compute-app
```

#### 3. 本番デプロイ（手動トリガー、承認必須）

```yaml
name: CloudFormation Deploy to Production

on:
  workflow_dispatch:  # 手動トリガーのみ
    inputs:
      stack-type:
        description: 'Stack type to deploy'
        required: true
        type: choice
        options:
          - 01-network
          - 02-database
          - 03-compute-base
          - 04-compute-app

jobs:
  deploy-prd:
    runs-on: ubuntu-latest
    environment:
      name: production  # GitHub環境保護ルール適用（承認必須）
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID_PRD }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY_PRD }}
          aws-region: ap-northeast-1

      - name: Create Change Set
        run: ./scripts/create-changeset.sh prd ${{ github.event.inputs.stack-type }}

      - name: Describe Change Set
        run: ./scripts/describe-changeset.sh prd ${{ github.event.inputs.stack-type }}

      # GitHub環境保護ルールで承認必須（01-network は複数人承認推奨）
      - name: Execute Change Set
        run: ./scripts/execute-changeset.sh prd ${{ github.event.inputs.stack-type }}

      - name: Save Change Set log to S3
        run: ./scripts/save-changeset-log.sh prd ${{ github.event.inputs.stack-type }}
```

**GitHub環境保護ルールの設定例**:

| 環境 | スタック | 必要な承認者数 | 承認者 |
|-----|---------|-------------|--------|
| production | 01-network | 2人以上 | SRE Lead + 開発Lead |
| production | 02-database | 1人 | SRE Lead |
| production | 03-compute-base | 1人 | SRE Lead |
| production | 04-compute-app | 1人 | SRE or Lead Dev |
```

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/2.4.6_IaC構築プロセス/2.4.6.1_CloudFormation構築/`
