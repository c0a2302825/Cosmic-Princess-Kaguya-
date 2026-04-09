from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import os

# 環境変数からURLを取得（Docker用）、なければローカル用を使用
DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:kaguya_pass@127.0.0.1:3307/kaguya_db?charset=utf8mb4")

engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """MySQLの起動を待ってテーブルを作成する"""
    connected = False
    while not connected:
        try:
            Base.metadata.create_all(bind=engine)
            connected = True
            print("Connected to MySQL successfully!")
        except Exception as e:
            print(f"Waiting for MySQL... ({e})")
            time.sleep(5)