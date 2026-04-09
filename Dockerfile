# Python 3.12の軽量イメージを使用
FROM python:3.12-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# MySQL接続に必要なパッケージをインストール
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 依存ライブラリのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir google-genai

# ソースコードのコピー
COPY . .

# アプリケーションの起動
CMD ["python", "kaguya_app.py"]