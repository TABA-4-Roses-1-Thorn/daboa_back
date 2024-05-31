from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import declarative_base
from pydantic import EmailStr

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
class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    ai_message = Column(String, nullable=True)

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

