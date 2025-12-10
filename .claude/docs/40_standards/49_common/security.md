# セキュリティ・運用基準

## 基本方針

- **シークレット情報のハードコード禁止**
- **最小権限の原則**
- **多層防御**

---

## シークレット管理

### AWS Secrets Manager（推奨）

```python
# ✅ Good
import boto3
import json

def get_db_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='myapp/database')
    return json.loads(response['SecretString'])

# 使用例
creds = get_db_credentials()
db_url = f"postgresql://{creds['username']}:{creds['password']}@{creds['host']}/myapp"
```

### 環境変数（開発環境）

```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/myapp
API_KEY=xxx

# .env.example（Gitにコミット）
DATABASE_URL=postgresql://user:pass@localhost/myapp
API_KEY=your_api_key_here
```

### .gitignore必須

```gitignore
# .gitignore
.env
*.pem
*.key
secrets.json
credentials.json
```

---

## セキュリティチェックリスト

### アプリケーション

- [ ] SQLインジェクション対策（パラメータ化クエリ）
- [ ] XSS対策（エスケープ処理）
- [ ] CSRF対策（トークン検証）
- [ ] パスワードハッシュ化（bcrypt、Argon2）
- [ ] HTTPS強制
- [ ] セキュリティヘッダー設定
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Content-Security-Policy
  - Strict-Transport-Security

### インフラ

- [ ] SecurityGroupの最小化（必要なポートのみ開放）
- [ ] IAMロールの最小権限
- [ ] VPC内のプライベートサブネット使用
- [ ] RDS暗号化有効化
- [ ] S3バケットのパブリックアクセス無効化
- [ ] CloudTrail有効化（監査ログ）
- [ ] GuardDuty有効化（脅威検出）

### 依存関係

- [ ] npm audit / pip-audit 実行
- [ ] Snyk / Trivy でスキャン
- [ ] Dependabot有効化

---

## 監視・ログ

### CloudWatch設定

```yaml
# 必須メトリクス
- CPU使用率 > 80%
- メモリ使用率 > 80%
- ディスク使用率 > 80%
- エラー率 > 1%
- レスポンスタイム > 1秒
```

### ログ管理

```python
# ✅ Good: 構造化ログ
import logging
import json

logger = logging.getLogger(__name__)

logger.info(json.dumps({
    "event": "user_login",
    "user_id": 123,
    "timestamp": "2025-10-19T10:00:00Z"
}))

# ❌ Bad: シークレット情報をログ出力
logger.info(f"API Key: {api_key}")  # ❌ 禁止
```

---

## バックアップ・復旧

### RDS自動バックアップ

```yaml
BackupRetentionPeriod: 7  # 7日間保持
PreferredBackupWindow: "03:00-04:00"  # 深夜3-4時
```

### 復旧目標

- **RTO（復旧時間目標）**: 1時間以内
- **RPO（復旧ポイント目標）**: 5分以内

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/2.4.7_シークレット管理実装.md`
