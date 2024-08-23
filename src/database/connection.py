from urllib.parse import quote

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 데이터베이스 URL을 설정
user = "admin"
pwd = ""
host = ""
port = 3306
db_name = "daboaDB"
DATABASE_URL = f'mysql+pymysql://{user}:{quote(pwd)}@{host}:{port}/{db_name}?charset=utf8'

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():   # 세션 처리
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
