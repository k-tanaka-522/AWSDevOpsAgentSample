#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation スタック削除
# ==============================================================================
# 使い方:
#   ./scripts/delete-stack.sh 04-monitoring
#   ./scripts/delete-stack.sh 03-compute
#   ./scripts/delete-stack.sh 02-database
#   ./scripts/delete-stack.sh 01-security
#   ./scripts/delete-stack.sh 00-base
#
# 注意: 依存関係の逆順で削除してください
# ==============================================================================

STACK_TYPE=$1

if [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <stack-type>"
  echo "  Example: $0 04-monitoring"
  echo ""
  echo "Delete order (reverse dependency):"
  echo "  1. ./scripts/delete-stack.sh 04-monitoring"
  echo "  2. ./scripts/delete-stack.sh 03-compute"
  echo "  3. ./scripts/delete-stack.sh 02-database"
  echo "  4. ./scripts/delete-stack.sh 01-security"
  echo "  5. ./scripts/delete-stack.sh 00-base"
  exit 1
fi

PROJECT_NAME="xray-poc"
STACK_NAME="${PROJECT_NAME}-${STACK_TYPE}"
REGION="ap-northeast-1"

echo "===================================="
echo "Deleting Stack"
echo "===================================="
echo "Stack: ${STACK_NAME}"
echo "===================================="
echo ""
echo "⚠️  WARNING: This will delete all resources in the stack!"
echo ""

# スタック存在確認
if ! aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${REGION} &>/dev/null; then
  echo "Stack '${STACK_NAME}' does not exist."
  exit 0
fi

# スタック情報表示
echo "Current stack resources:"
aws cloudformation describe-stack-resources \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --query 'StackResources[*].[LogicalResourceId,ResourceType,ResourceStatus]' \
  --output table

echo ""
read -p "Are you sure you want to delete stack '${STACK_NAME}'? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Deletion cancelled."
  exit 0
fi

echo "Deleting stack: ${STACK_NAME}"

aws cloudformation delete-stack \
  --stack-name ${STACK_NAME} \
  --region ${REGION}

echo "Waiting for stack deletion..."
aws cloudformation wait stack-delete-complete \
  --stack-name ${STACK_NAME} \
  --region ${REGION}

echo "✅ Stack deleted: ${STACK_NAME}"
