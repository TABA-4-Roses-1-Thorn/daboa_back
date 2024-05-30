from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:taba@127.0.0.1:3306/taba"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():   # 세션 처리
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()