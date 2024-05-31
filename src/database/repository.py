import cv2
from fastapi import Depends
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session
from pydantic import EmailStr

from database.connection import get_db
from database.orm import User, Setting, DateTime, EventlogSchedule
from schema.response import EventlogCreate

from schema.setting_schema import SettingUpdate,UserUpdate,SettingCreate

from datetime import datetime

from database.orm import Frame, Anomaly, Eventlog



class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_email(self, email: EmailStr) -> User | None:
        return self.session.scalar(
            select(User).where(User.email == email)
        )

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user

    def get_user(db: Session, user_id: int):
        return db.query(User.User).filter(User.User.id == user_id).first()

    def update_user(db: Session, user_id: int, user: UserUpdate):
        db_user = db.query(User.User).filter(User.User.id == user_id).first()
        db_user.username = user.username
        db_user.email = user.email
        db_user.password = user.password
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_setting(db: Session, setting: SettingCreate, user_id: int):
        db_setting = Setting(**setting.dict(), user_id=user_id)
        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)
        return db_setting

    def update_setting(db: Session, setting: SettingUpdate, setting_id: int):
        db_setting = db.query(Setting).filter(Setting.id == setting_id).first()
        db_setting.ai_message = setting.ai_message
        db.commit()
        db.refresh(db_setting)
        return db_setting

class RealStreamRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_frame_to_db(self, frame):
        # Generate timestamp and file path
        timestamp = func.now()
        file_path = f"frames/{timestamp}.jpg"

        # Save frame to file
        cv2.imwrite(file_path, frame)

        # Save frame metadata to the database
        frame_record = Frame(file_path=file_path, detection_score=0.0, timestamp=timestamp)
        self.session.add(frame_record)
        self.session.commit()
        self.session.refresh(frame_record)

        return frame_record

    def save_anomaly_to_db(self, frame_record_id):
        # Save anomaly metadata to the database
        timestamp = func.now()
        anomaly_record = Anomaly(frame_id=frame_record_id, timestamp=timestamp)
        self.session.add(anomaly_record)
        self.session.commit()

class EventlogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_date_time(self, date_time: datetime):
        db_datetime = EventlogSchedule(date_time=date_time)
        self.session.add(db_datetime)
        self.session.commit()
        self.session.refresh(db_datetime)
        return db_datetime
