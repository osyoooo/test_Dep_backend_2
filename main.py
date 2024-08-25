from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()

# 環境変数から接続情報を取得
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_SSL_CA = os.getenv('DB_SSL_CA')

# 接続文字列を生成
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
if DB_SSL_CA:
    DATABASE_URL += f"?ssl_ca={DB_SSL_CA}"

app = FastAPI()
Base = declarative_base()

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"データベース接続エラー: {e}")
    raise

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50))

Base.metadata.create_all(bind=engine)

@app.get("/users/")
def read_users():
    try:
        with SessionLocal() as session:
            from sqlalchemy.sql import select
            stmt = select(User)
            result = session.execute(stmt)
            users = result.scalars().all()
            return {"users": [{"name": user.name, "email": user.email} for user in users]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
