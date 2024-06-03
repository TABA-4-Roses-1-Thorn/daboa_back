from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import declarative_base, Session
from pydantic import EmailStr
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)

    @classmethod
    def create(cls, username: str, email: EmailStr, hashed_password: str) -> "User":
        return cls(
            username=username,
            email=email,
            password=hashed_password,
        )

    @classmethod
    def edit(cls, db: Session, user_id: int, username: str = None, email: str = None, password: str = None) -> "User":
        user = db.query(cls).filter(cls.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.password = password

        db.commit()
        db.refresh(user)
        return user
class AiMessage(Base):
    __tablename__ = "ai_message"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)

class Frame(Base):
    __tablename__ = "frames"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    file_path = Column(String, index=True)
    detection_score = Column(Float)

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    frame_id = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class EventlogSchedule(Base):
    __tablename__ = "eventlog_schedule"

    id = Column(Integer, primary_key=True, index=True)
    date_time = Column(DateTime, nullable=False)

class Eventlog(Base):
    __tablename__ = "eventlog"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)
    state = Column(Boolean, default=False)
    video = Column(String, nullable=True)
