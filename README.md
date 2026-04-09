# 超かぐや姫！グッズ管理アプリ

「超かぐや姫！」のグッズを管理するためのシンプルなウェブアプリケーションです。

## 機能

- グッズの追加、編集、削除
- カテゴリ別管理（フィギュア、ポスター、Tシャツ、アクセサリー、その他）
- 在庫数管理
- 価格管理
- 説明文と画像URLの登録

## 技術スタック

- **バックエンド**: Flask (Python)
- **データベース**: MySQL
- **ORM**: SQLAlchemy
- **コンテナ化**: Docker & Docker Compose
- **AI統合**: Google Gemini API (将来拡張用)

## セットアップと実行

### 前提条件

- Docker と Docker Compose がインストールされていること

### 実行手順

1. リポジトリをクローンまたはダウンロード
2. プロジェクトディレクトリに移動
3. Docker Compose で起動:

```bash
docker-compose up --build
```

4. ブラウザで `http://localhost:5002` にアクセス

### データベース

- MySQL 8.0 が自動的に起動
- データベース名: `kaguya_db`
- 初回起動時にテーブルが自動作成されます

## 開発モードでの実行

Dockerを使わずローカルで実行する場合:

1. Python 3.12 をインストール
2. 依存ライブラリをインストール:

```bash
pip install -r requirements.txt
```

3. MySQLサーバーを起動（ポート3307）
4. アプリを実行:

```bash
python kaguya_app.py
```

## API エンドポイント

- `GET /`: グッズ一覧表示
- `GET/POST /add`: グッズ追加
- `GET/POST /edit/<id>`: グッズ編集
- `GET /delete/<id>`: グッズ削除

## 環境変数

`.env` ファイルで設定:

- `SECRET_KEY`: Flaskのセッションキー
- `DB_URL`: データベース接続URL
- `GEMINI_API_KEY`: Google Gemini APIキー（将来のAI機能用）

## ライセンス

このプロジェクトは個人使用を目的としています。
