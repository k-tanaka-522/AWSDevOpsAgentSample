# Terraform 規約

## 基本方針

- **terraform plan必須**（dry-run）
- **S3 + DynamoDBでstate管理**
- **モジュール化**

---

## プロジェクト構成

```
infra/terraform/
├── modules/
│   ├── vpc/
│   ├── ecs/
│   └── rds/
├── environments/
│   ├── dev/
│   ├── stg/
│   └── prd/
└── backend.tf
```

---

## State管理（S3 + DynamoDB）

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

### State管理リソース作成

```bash
# S3バケット作成
aws s3 mb s3://myapp-terraform-state --region ap-northeast-1
aws s3api put-bucket-versioning \
  --bucket myapp-terraform-state \
  --versioning-configuration Status=Enabled

# DynamoDBテーブル作成
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## デプロイ手順（terraform plan必須）

```bash
# ❌ Bad: 直接apply
terraform apply

# ✅ Good: planで確認
# 1. 初期化
terraform init

# 2. plan（dry-run）
terraform plan -out=tfplan

# 3. 確認後、apply
terraform apply tfplan
```

---

## モジュール化

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
  tags = {
    Name        = "${var.project_name}-${var.environment}-vpc"
    Environment = var.environment
  }
}

# environments/prd/main.tf
module "vpc" {
  source = "../../modules/vpc"

  project_name = "myapp"
  environment  = "prd"
  cidr_block   = "10.0.0.0/16"
}
```

---

## Workspace管理

```bash
# Workspace作成
terraform workspace new dev
terraform workspace new stg
terraform workspace new prd

# Workspace切り替え
terraform workspace select prd

# 現在のWorkspace確認
terraform workspace show
```

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/2.4.6_IaC構築プロセス/2.4.6.2_Terraform構築/`
