# X-Ray Watch POC - Pythonアプリケーション
#
# 目的・理由:
# - FastAPIアプリケーションをコンテナ化
# - AWS X-Ray Daemonと連携
# - ECS環境でデプロイ可能
#
# 影響範囲:
# - ECSタスク（アプリケーションコンテナ）
#
# 前提条件・制約:
# - Python 3.11を使用
# - X-Ray DaemonがサイドカーコンテナとしてECSタスクに含まれること

FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# ポート公開
EXPOSE 8000

# Uvicornでアプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
