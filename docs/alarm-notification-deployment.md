# CloudWatch Alarm HTML Email Notification - Deployment Guide

## Overview
CloudWatch AlarmからSNS経由でLambda関数をトリガーし、HTMLフォーマットされたメール通知をSES経由で送信するシステムです。

## Architecture
```
CloudWatch Alarm → SNS Topic → Lambda Function → SES → Email (HTML)
```

## Deployed Resources

### CloudFormation Stack
- **Stack Name**: `xray-poc-alarm-formatter`
- **Region**: ap-northeast-1
- **Template**: `infra/cloudformation/stacks/05-alarm-formatter.yaml`

### Resources Created
| Resource Type | Resource Name | Purpose |
|--------------|---------------|---------|
| IAM Role | xray-poc-alarm-formatter-role | Lambda execution role with SES permissions |
| Lambda Function | xray-poc-alarm-formatter | Format CloudWatch Alarms to HTML emails |
| SNS Subscription | Lambda subscription to xray-poc-alerts | Trigger Lambda from SNS |
| Lambda Permission | SNS invoke permission | Allow SNS to trigger Lambda |
| CloudWatch Alarm | xray-poc-test-alarm | Test alarm for email notifications |

## Prerequisites

### 1. SES Email Verification
The email address must be verified in Amazon SES:

```bash
# Verify email address
aws ses verify-email-identity \
  --email-address yotkn003@gmail.com \
  --region ap-northeast-1

# Check verification status
aws ses get-identity-verification-attributes \
  --identities yotkn003@gmail.com \
  --region ap-northeast-1
```

**Expected Output**:
```json
{
    "VerificationAttributes": {
        "yotkn003@gmail.com": {
            "VerificationStatus": "Success"
        }
    }
}
```

**Note**: Check your email inbox and click the verification link sent by AWS SES.

### 2. Existing SNS Topic
- **Topic ARN**: `arn:aws:sns:ap-northeast-1:897167645238:xray-poc-alerts`
- **Subscription**: Email subscription to yotkn003@gmail.com (confirmed)

## Deployment Steps

### 1. Validate CloudFormation Template
```bash
cd infra/cloudformation/stacks

# Ensure file has LF line endings (not CRLF)
dos2unix 05-alarm-formatter.yaml

# Remove non-ASCII characters if any
sed -i 's/→/->/g' 05-alarm-formatter.yaml

# Validate template
aws cloudformation validate-template \
  --template-body file://05-alarm-formatter.yaml \
  --region ap-northeast-1
```

### 2. Create CloudFormation Stack
```bash
aws cloudformation create-stack \
  --stack-name xray-poc-alarm-formatter \
  --template-body file://05-alarm-formatter.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1
```

### 3. Wait for Stack Creation
```bash
aws cloudformation wait stack-create-complete \
  --stack-name xray-poc-alarm-formatter \
  --region ap-northeast-1

# Check status
aws cloudformation describe-stacks \
  --stack-name xray-poc-alarm-formatter \
  --region ap-northeast-1 \
  --query 'Stacks[0].StackStatus' \
  --output text
```

**Expected**: `CREATE_COMPLETE`

### 4. Verify Resources
```bash
aws cloudformation describe-stack-resources \
  --stack-name xray-poc-alarm-formatter \
  --region ap-northeast-1 \
  --query 'StackResources[*].[ResourceType,LogicalResourceId,PhysicalResourceId,ResourceStatus]' \
  --output table
```

## Testing

### 1. Trigger Test Alarm (ALARM State)
```bash
aws cloudwatch set-alarm-state \
  --alarm-name xray-poc-test-alarm \
  --state-value ALARM \
  --state-reason "Manual test trigger for HTML email notification" \
  --region ap-northeast-1
```

### 2. Trigger Test Alarm (OK State)
```bash
aws cloudwatch set-alarm-state \
  --alarm-name xray-poc-test-alarm \
  --state-value OK \
  --state-reason "Manual test trigger for OK state notification" \
  --region ap-northeast-1
```

### 3. Check Lambda Logs
```bash
# Get latest log stream
MSYS_NO_PATHCONV=1 aws logs describe-log-streams \
  --log-group-name /aws/lambda/xray-poc-alarm-formatter \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --region ap-northeast-1 \
  --query 'logStreams[0].logStreamName' \
  --output text

# View logs (replace LOG_STREAM_NAME with actual value)
MSYS_NO_PATHCONV=1 aws logs get-log-events \
  --log-group-name /aws/lambda/xray-poc-alarm-formatter \
  --log-stream-name 'LOG_STREAM_NAME' \
  --region ap-northeast-1 \
  --query 'events[*].message' \
  --output text
```

**Expected Log Output**:
```
Email sent: 0106019b11412929-e63861ff-ba5f-4c52-ac9f-bf408e9435b0-000000
```

### 4. Check Email
Check the inbox of `yotkn003@gmail.com` for HTML-formatted emails with:
- **Subject**: `[ALARM] CloudWatch: xray-poc-test-alarm` or `[OK] CloudWatch: xray-poc-test-alarm`
- **Content**: Modern HTML design with:
  - Red background for ALARM state
  - Green background for OK state
  - Alarm details (name, description, reason, timestamp)
  - "View in AWS Console" button linking to CloudWatch console

## HTML Email Design

The Lambda function generates HTML emails with the following features:

### Color Schemes by State
| State | Header Color | Badge Color | Icon |
|-------|-------------|-------------|------|
| ALARM | Red (#dc3545) | Light red (#f8d7da) | ⚠ |
| OK | Green (#198754) | Light green (#d1e7dd) | ✓ |
| INSUFFICIENT_DATA | Yellow (#ffc107) | Light yellow (#fff3cd) | ? |

### Email Sections
1. **Header**: Large icon, "CloudWatch Alarm" title, state badge
2. **Alarm Name**: H2 heading
3. **Description**: Info section with alarm description
4. **State Change**: Visual representation of state transition (OLD -> NEW)
5. **Reason**: Detailed reason for state change
6. **Timestamp**: When the state change occurred
7. **Action Button**: "View in AWS Console" link to CloudWatch alarm
8. **Footer**: Project identifier

## Update Stack (Change Set Method)

### 1. Create Change Set
```bash
cd infra/cloudformation

# Update template if needed
# Then create change set
bash scripts/create-changeset.sh 05-alarm-formatter
```

### 2. Review Change Set
```bash
bash scripts/describe-changeset.sh 05-alarm-formatter
```

### 3. Execute Change Set
```bash
bash scripts/execute-changeset.sh 05-alarm-formatter
```

## Rollback

### Delete Stack
```bash
aws cloudformation delete-stack \
  --stack-name xray-poc-alarm-formatter \
  --region ap-northeast-1

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name xray-poc-alarm-formatter \
  --region ap-northeast-1
```

**Note**: This will delete all resources including:
- Lambda function
- IAM role
- SNS subscription
- Test CloudWatch alarm

The SNS topic and SES verified email will remain unchanged.

## Troubleshooting

### Email Not Received
1. **Check SES verification status**:
   ```bash
   aws ses get-identity-verification-attributes \
     --identities yotkn003@gmail.com \
     --region ap-northeast-1
   ```
   Ensure `VerificationStatus` is `Success`.

2. **Check Lambda execution**:
   - View CloudWatch Logs for the Lambda function
   - Look for errors or exceptions

3. **Check SNS subscription**:
   ```bash
   aws sns list-subscriptions-by-topic \
     --topic-arn arn:aws:sns:ap-northeast-1:897167645238:xray-poc-alerts \
     --region ap-northeast-1
   ```
   Ensure Lambda subscription exists and is confirmed.

### Lambda Permission Error
If Lambda is not triggered by SNS, check:
```bash
aws lambda get-policy \
  --function-name xray-poc-alarm-formatter \
  --region ap-northeast-1
```
Ensure SNS has permission to invoke the Lambda function.

### Template Encoding Error
If `aws cloudformation validate-template` fails with encoding error:
```bash
# Convert line endings to LF
dos2unix 05-alarm-formatter.yaml

# Remove Unicode characters
sed -i 's/→/->/g' 05-alarm-formatter.yaml

# Verify file encoding
file 05-alarm-formatter.yaml
```
Expected: `ASCII text` or `UTF-8 text` (not with "very long lines")

## Cost Estimate

### Monthly Costs (assuming 1000 alarms/month)
| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 1000 invocations, 256MB, 250ms avg | ~$0.00 (within free tier) |
| SES | 1000 emails | ~$0.10 |
| CloudWatch Logs | ~10MB logs | ~$0.01 |
| SNS | 1000 notifications to Lambda | ~$0.00 (within free tier) |
| **Total** | | **~$0.11/month** |

**Note**: Costs may vary based on actual usage. Free tier limits:
- Lambda: 1M requests/month, 400,000 GB-seconds/month
- SES: 62,000 emails/month (if sending from EC2)
- SNS: 1M publishes/month

## Security Considerations

1. **IAM Least Privilege**: Lambda execution role only has SES send permissions
2. **Email Verification**: SES requires verified sender email (prevents spam)
3. **SNS Authentication**: Lambda permission restricts invocation to specific SNS topic ARN
4. **CloudWatch Logs**: All Lambda executions logged for audit trail

## Monitoring

### Key Metrics to Monitor
- **Lambda Invocations**: Number of times Lambda is triggered
- **Lambda Errors**: Failed executions
- **Lambda Duration**: Execution time (should be <300ms)
- **SES Bounce Rate**: Failed email deliveries

### CloudWatch Alarms (Recommended)
```bash
# Lambda Error Rate Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name lambda-formatter-errors \
  --alarm-description "Alert on Lambda function errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --dimensions Name=FunctionName,Value=xray-poc-alarm-formatter \
  --region ap-northeast-1
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-12 | Initial release with HTML email formatting |

## References

- [Lambda Function Code](../infra/lambda/alarm-formatter/handler.py)
- [CloudFormation Template](../infra/cloudformation/stacks/05-alarm-formatter.yaml)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [CloudWatch Alarms Documentation](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
