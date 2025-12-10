#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set詳細表示（dry-run）
# ==============================================================================
# 使い方:
#   ./scripts/describe-changeset.sh 00-base
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
echo "Change Set Details (dry-run)"
echo "===================================="
echo "Stack:      ${STACK_NAME}"
echo "Change Set: ${CHANGE_SET_NAME}"
echo "===================================="
echo ""

# Change Set詳細表示
aws cloudformation describe-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --region ${REGION} \
  --query 'Changes[].{Action:ResourceChange.Action,LogicalId:ResourceChange.LogicalResourceId,Type:ResourceChange.ResourceType,Replacement:ResourceChange.Replacement}' \
  --output table

echo ""
echo "ℹ️  This is a dry-run. No changes were applied."
echo ""
echo "To apply these changes, run:"
echo "   ./scripts/execute-changeset.sh ${STACK_TYPE}"
echo ""
echo "To cancel this Change Set, run:"
echo "   aws cloudformation delete-change-set --stack-name ${STACK_NAME} --change-set-name ${CHANGE_SET_NAME} --region ${REGION}"
