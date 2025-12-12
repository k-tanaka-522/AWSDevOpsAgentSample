import json
import boto3
from datetime import datetime
from typing import Dict, Any

ses_client = boto3.client('ses', region_name='ap-northeast-1')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CloudWatch Alarm SNS通知をHTMLメールに変換して送信
    """
    try:
        # SNSメッセージをパース
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])

        # アラーム情報を抽出
        alarm_name = sns_message.get('AlarmName', 'Unknown Alarm')
        new_state = sns_message.get('NewStateValue', 'UNKNOWN')
        old_state = sns_message.get('OldStateValue', 'UNKNOWN')
        reason = sns_message.get('NewStateReason', 'No reason provided')
        timestamp = sns_message.get('StateChangeTime', datetime.utcnow().isoformat())
        alarm_description = sns_message.get('AlarmDescription', 'No description')

        # AWS Console URLを生成
        region = sns_message.get('Region', 'ap-northeast-1')
        account_id = context.invoked_function_arn.split(':')[4]
        alarm_url = f"https://console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{alarm_name}"

        # HTMLメールを生成
        html_body = generate_html_email(
            alarm_name=alarm_name,
            new_state=new_state,
            old_state=old_state,
            reason=reason,
            timestamp=timestamp,
            description=alarm_description,
            alarm_url=alarm_url
        )

        # メール送信
        response = ses_client.send_email(
            Source='yotkn003@gmail.com',
            Destination={
                'ToAddresses': ['yotkn003@gmail.com']
            },
            Message={
                'Subject': {
                    'Data': f"[{new_state}] CloudWatch Alarm: {alarm_name}",
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        print(f"Email sent successfully. MessageId: {response['MessageId']}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Email sent successfully',
                'messageId': response['MessageId']
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise


def generate_html_email(alarm_name: str, new_state: str, old_state: str,
                       reason: str, timestamp: str, description: str,
                       alarm_url: str) -> str:
    """
    モダンなHTMLメールを生成
    """

    # 状態に応じた色とアイコンを設定
    state_config = {
        'ALARM': {
            'color': '#dc3545',
            'bg_color': '#f8d7da',
            'icon': '⚠',
            'text': 'ALARM'
        },
        'OK': {
            'color': '#198754',
            'bg_color': '#d1e7dd',
            'icon': '✓',
            'text': 'OK'
        },
        'INSUFFICIENT_DATA': {
            'color': '#ffc107',
            'bg_color': '#fff3cd',
            'icon': '?',
            'text': 'INSUFFICIENT DATA'
        }
    }

    config = state_config.get(new_state, state_config['INSUFFICIENT_DATA'])

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background-color: {config['color']};
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .state-badge {{
            display: inline-block;
            background-color: {config['bg_color']};
            color: {config['color']};
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin: 10px 0;
        }}
        .info-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid {config['color']};
            border-radius: 4px;
        }}
        .info-label {{
            font-weight: 600;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .info-value {{
            color: #333;
            font-size: 14px;
            margin-bottom: 15px;
        }}
        .info-value:last-child {{
            margin-bottom: 0;
        }}
        .state-change {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 20px 0;
            font-size: 14px;
        }}
        .state-change span {{
            padding: 5px 15px;
            border-radius: 15px;
            background-color: #e9ecef;
            margin: 0 10px;
        }}
        .arrow {{
            font-size: 20px;
            color: #666;
        }}
        .button {{
            display: inline-block;
            background-color: {config['color']};
            color: white;
            text-decoration: none;
            padding: 12px 30px;
            border-radius: 6px;
            margin: 20px 0;
            font-weight: 600;
            text-align: center;
        }}
        .button:hover {{
            opacity: 0.9;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #dee2e6;
        }}
        .timestamp {{
            color: #999;
            font-size: 13px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">{config['icon']}</div>
            <h1>CloudWatch Alarm Notification</h1>
            <div class="state-badge">{config['text']}</div>
        </div>

        <div class="content">
            <h2 style="color: #333; margin-top: 0;">{alarm_name}</h2>

            <div class="info-section">
                <div class="info-label">Description</div>
                <div class="info-value">{description}</div>
            </div>

            <div class="state-change">
                <span>{old_state}</span>
                <span class="arrow">→</span>
                <span style="background-color: {config['bg_color']}; color: {config['color']}; font-weight: 600;">{new_state}</span>
            </div>

            <div class="info-section">
                <div class="info-label">Reason</div>
                <div class="info-value">{reason}</div>
            </div>

            <div class="info-section">
                <div class="info-label">Timestamp</div>
                <div class="info-value">{timestamp}</div>
            </div>

            <div style="text-align: center;">
                <a href="{alarm_url}" class="button">View in AWS Console</a>
            </div>
        </div>

        <div class="footer">
            <p>This is an automated notification from AWS CloudWatch Alarms</p>
            <p>X-Ray Watch POC - Monitoring System</p>
        </div>
    </div>
</body>
</html>
"""

    return html
