from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import os

# 環境変数からURLを取得（Docker用）、なければSQLite用を使用（ローカル開発用）
if os.getenv("DB_URL"):
    DB_URL = os.getenv("DB_URL")
else:
    # ローカル開発用SQLite
    DB_URL = "sqlite:///./kaguya_db.sqlite"

# SQLiteの場合は特別な設定が必要
if "sqlite" in DB_URL:
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """データベースの起動を待ってテーブルを作成する"""
    connected = False
    while not connected:
        try:
            Base.metadata.create_all(bind=engine)
            
            # release_dateカラムがない場合は追加
            try:
                with engine.connect() as conn:
                    if "sqlite" in DB_URL:
                        # SQLiteの場合は PRAGMA で確認
                        result = conn.execute(text("PRAGMA table_info(goods)"))
                        columns = [row[1] for row in result]
                        if "release_date" not in columns:
                            print("Adding release_date column to goods table...")
                            conn.execute(text("ALTER TABLE goods ADD COLUMN release_date DATE DEFAULT NULL"))
                            conn.commit()
                            print("release_date column added successfully!")
                    else:
                        # MySQLの場合
                        try:
                            conn.execute(text("ALTER TABLE goods ADD COLUMN release_date DATE DEFAULT NULL"))
                            conn.commit()
                            print("release_date column added successfully!")
                        except Exception as e:
                            if "Duplicate column" in str(e) or "already exists" in str(e):
                                print("release_date column already exists")
                            else:
                                raise
            except Exception as e:
                print(f"Column migration note: {e}")
            
            connected = True
            print("Connected to database successfully!")
        except Exception as e:
            print(f"Waiting for database... ({e})")
            time.sleep(1)