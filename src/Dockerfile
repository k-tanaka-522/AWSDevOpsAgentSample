FROM python:3.11-slim

# 目的: X-Ray Watch POC用のFastAPIアプリケーションコンテナ
# 理由: Python 3.11-slimで軽量化、ポート80でALBからのリクエストを受け付ける
# 影響範囲: ECS Fargateで実行される
# 前提条件: DATABASE_URL、AWS_XRAY_DAEMON_ADDRESS環境変数が設定されていること

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート80で起動（ALBのヘルスチェックがポート80を想定）
EXPOSE 80

# uvicornでFastAPIを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
