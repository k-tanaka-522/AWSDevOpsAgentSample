#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set実行
# ==============================================================================
# 使い方:
#   ./scripts/execute-changeset.sh 00-base
# ==============================================================================

STACK_TYPE=$1

if [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <stack-type>"
  echo "  Example: $0 00-base"
  exit 1
fi

PROJECT_NAME="xray-poc"
STACK_NAME="${PROJECT_NAME}-${STACK_TYPE}"
REGION="ap-northeast-1"

if [ ! -f "/tmp/changeset-${STACK_NAME}.txt" ]; then
  echo "Error: Change Set not found. Please run create-changeset.sh first."
  exit 1
fi

CHANGE_SET_NAME=$(cat /tmp/changeset-${STACK_NAME}.txt)

echo "===================================="
echo "Executing Change Set"
echo "===================================="
echo "Stack:      ${STACK_NAME}"
echo "Change Set: ${CHANGE_SET_NAME}"
echo "===================================="
echo ""

# 承認プロンプト
read -p "Execute Change Set '${CHANGE_SET_NAME}' on ${STACK_NAME}? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Deployment cancelled."
  exit 0
fi

echo "Executing Change Set: ${CHANGE_SET_NAME}"

aws cloudformation execute-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --region ${REGION}

echo "Waiting for stack operation to complete..."

# スタックの状態確認（CREATE or UPDATE）
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${REGION} --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "UNKNOWN")

if [[ "$STACK_STATUS" == "CREATE_IN_PROGRESS" ]]; then
  aws cloudformation wait stack-create-complete \
    --stack-name ${STACK_NAME} \
    --region ${REGION}
else
  aws cloudformation wait stack-update-complete \
    --stack-name ${STACK_NAME} \
    --region ${REGION}
fi

echo "✅ Deployment completed: ${STACK_NAME}"
rm -f /tmp/changeset-${STACK_NAME}.txt

# Outputs表示
echo ""
echo "Stack Outputs:"
aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --region ${REGION} \
  --query 'Stacks[0].Outputs' \
  --output table
