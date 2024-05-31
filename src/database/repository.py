from fastapi import Depends
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import Session
from pydantic import EmailStr, BaseModel

from database.connection import get_db
from database.orm import User, Setting, DateTime, EventlogSchedule, Eventlog
from schema.response import EventlogScheduleCreate
from schema.request import EventlogCreate

from schema.setting_schema import SettingUpdate,UserUpdate,SettingCreate

from datetime import datetime


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

class EventlogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_date_time(self, date_time: datetime):
        db_datetime = EventlogSchedule(date_time=date_time)
        self.session.add(db_datetime)
        self.session.commit()
        self.session.refresh(db_datetime)
        return db_datetime

    def create_eventlog(self, eventlog: EventlogCreate):
        db_eventlog = Eventlog(
            type=eventlog.type,
            time=eventlog.time,
            state=eventlog.state,
            video=eventlog.video
        )
        self.session.add(db_eventlog)
        self.session.commit()
        self.session.refresh(db_eventlog)
        return db_eventlog

    def get_eventlog(self, skip: int = 0, limit: int = 10, start_date: datetime = None, end_date: datetime = None):
        query = self.session.query(Eventlog)

        if start_date and end_date:
            query = query.filter(and_(Eventlog.time >= start_date, Eventlog.time <= end_date))
        elif start_date:
            query = query.filter(Eventlog.time >= start_date)
        elif end_date:
            query = query.filter(Eventlog.time <= end_date)

        return query.offset(skip).limit(limit).all()