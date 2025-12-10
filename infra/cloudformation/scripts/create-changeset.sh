#!/bin/bash
set -euo pipefail

# ==============================================================================
# CloudFormation Change Set作成
# ==============================================================================
# 使い方:
#   ./scripts/create-changeset.sh 00-base
#   ./scripts/create-changeset.sh 01-security
#   ./scripts/create-changeset.sh 02-database
#   ./scripts/create-changeset.sh 03-compute
#   ./scripts/create-changeset.sh 04-monitoring
# ==============================================================================

STACK_TYPE=$1

if [ -z "$STACK_TYPE" ]; then
  echo "Usage: $0 <stack-type>"
  echo "  Example: $0 00-base"
  echo "  Stack types: 00-base, 01-security, 02-database, 03-compute, 04-monitoring"
  exit 1
fi

PROJECT_NAME="xray-poc"
STACK_NAME="${PROJECT_NAME}-${STACK_TYPE}"
TEMPLATE_FILE="stacks/${STACK_TYPE}.yaml"
PARAMETERS_FILE="parameters/dev.json"
CHANGE_SET_NAME="deploy-$(date +%Y%m%d-%H%M%S)"
REGION="ap-northeast-1"

echo "===================================="
echo "Creating Change Set"
echo "===================================="
echo "Stack:      ${STACK_NAME}"
echo "Template:   ${TEMPLATE_FILE}"
echo "Parameters: ${PARAMETERS_FILE}"
echo "Change Set: ${CHANGE_SET_NAME}"
echo "===================================="

# 1. テンプレート検証
echo "Validating template..."
aws cloudformation validate-template \
  --template-body file://${TEMPLATE_FILE} \
  --region ${REGION} \
  > /dev/null

echo "✅ Template is valid"

# 2. スタック存在確認（作成 or 更新）
CHANGE_SET_TYPE="UPDATE"
if ! aws cloudformation describe-stacks --stack-name ${STACK_NAME} --region ${REGION} &>/dev/null; then
  CHANGE_SET_TYPE="CREATE"
  echo "Stack does not exist. Creating new stack..."
fi

# 3. Change Set作成
echo "Creating Change Set (${CHANGE_SET_TYPE})..."

# パラメータの読み込みと必要なパラメータのみ抽出
PARAMS_JSON=$(cat ${PARAMETERS_FILE})

# スタックタイプに応じてパラメータをフィルタリング
case "$STACK_TYPE" in
  "00-base")
    FILTERED_PARAMS=$(echo "$PARAMS_JSON" | jq '[.[] | select(.ParameterKey | IN("Environment", "VpcCidr", "PublicSubnetCidr", "DbSubnetCidr", "AvailabilityZone"))]')
    ;;
  "01-security")
    FILTERED_PARAMS=$(echo "$PARAMS_JSON" | jq '[.[] | select(.ParameterKey | IN("Environment", "GitHubOrg", "GitHubRepo"))] + [{"ParameterKey":"BaseStackName","ParameterValue":"xray-poc-00-base"}]')
    ;;
  "02-database")
    FILTERED_PARAMS=$(echo "$PARAMS_JSON" | jq '[.[] | select(.ParameterKey | IN("Environment", "DBInstanceClass", "DBAllocatedStorage", "DBBackupRetentionPeriod"))] + [{"ParameterKey":"BaseStackName","ParameterValue":"xray-poc-00-base"},{"ParameterKey":"SecurityStackName","ParameterValue":"xray-poc-01-security"}]')
    ;;
  "03-compute")
    FILTERED_PARAMS=$(echo "$PARAMS_JSON" | jq '[.[] | select(.ParameterKey | IN("Environment", "ECSTaskCpu", "ECSTaskMemory", "ECSDesiredCount", "ECSAssignPublicIp"))] + [{"ParameterKey":"BaseStackName","ParameterValue":"xray-poc-00-base"},{"ParameterKey":"SecurityStackName","ParameterValue":"xray-poc-01-security"},{"ParameterKey":"DatabaseStackName","ParameterValue":"xray-poc-02-database"}]')
    ;;
  "04-monitoring")
    FILTERED_PARAMS=$(echo "$PARAMS_JSON" | jq '[.[] | select(.ParameterKey | IN("Environment", "AlertEmail"))] + [{"ParameterKey":"DatabaseStackName","ParameterValue":"xray-poc-02-database"},{"ParameterKey":"ComputeStackName","ParameterValue":"xray-poc-03-compute"}]')
    ;;
  *)
    echo "Unknown stack type: $STACK_TYPE"
    exit 1
    ;;
esac

echo "$FILTERED_PARAMS" > /tmp/${STACK_NAME}-params.json

aws cloudformation create-change-set \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --template-body file://${TEMPLATE_FILE} \
  --parameters file:///tmp/${STACK_NAME}-params.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --change-set-type ${CHANGE_SET_TYPE} \
  --region ${REGION}

echo "Waiting for Change Set creation..."
aws cloudformation wait change-set-create-complete \
  --stack-name ${STACK_NAME} \
  --change-set-name ${CHANGE_SET_NAME} \
  --region ${REGION}

echo "✅ Change Set created: ${CHANGE_SET_NAME}"
echo "${CHANGE_SET_NAME}" > /tmp/changeset-${STACK_NAME}.txt
echo ""
echo "Next steps:"
echo "  1. Review changes: ./scripts/describe-changeset.sh ${STACK_TYPE}"
echo "  2. Execute changes: ./scripts/execute-changeset.sh ${STACK_TYPE}"

rm -f /tmp/${STACK_NAME}-params.json
