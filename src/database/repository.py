from http.client import HTTPException
from typing import List, Optional

import aioredis
import cv2
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from sqlalchemy import select, delete, and_, func, extract
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.orm import Session
from pydantic import EmailStr, BaseModel

from database.connection import get_db
from database.orm import User, DateTime, EventlogSchedule, Eventlog
from schema.response import EventlogScheduleCreate
from schema.request import EventlogCreate
from service.utils import get_all_months, get_all_weeks, get_all_days, get_all_hours
from schema.setting_schema import SettingUpdate,UserUpdate,SettingCreate


from datetime import datetime, timedelta

from database.orm import Frame, Anomaly, Eventlog

from service.security import TokenData

SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Redis 연결
redis = aioredis.from_url("redis://localhost:6379")
class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user

    def get_user(self, user_id: int) -> User | None:
        return self.session.scalar(
            select(User).where(User.id == user_id)
        )

    def edit_user(self, user_id: int, username: str = None, email: str = None, password: str = None) -> User:
        return User.edit(
            db=self.session,
            user_id=user_id,
            username=username,
            email=email,
            password=password
        )

    def delete_user(self, user_id: int) -> None:
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
        else:
            raise ValueError("User not found")





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

    def get_all_eventlogs(self) -> List[Eventlog]:
        return self.session.query(Eventlog).all()

class AnalyticsRepository:
    def __init__(self, session: Session):
        self.session = session

    # 지난 월/주/일 대비 이상행동 건수
    def get_monthly_stats(self):
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        previous_month = start_of_month - timedelta(days=1)
        start_of_previous_month = datetime(previous_month.year, previous_month.month, 1)

        current_month_count = self.session.query(func.count(Eventlog.id)).filter(
            Eventlog.time >= start_of_month).scalar()
        previous_month_count = self.session.query(func.count(Eventlog.id)).filter(
            Eventlog.time >= start_of_previous_month, Eventlog.time < start_of_month).scalar()

        return {
            "current_month": current_month_count,
            "previous_month": previous_month_count,
            "change": (current_month_count - previous_month_count) / previous_month_count * 100 if previous_month_count else 0
        }

    def get_weekly_stats(self):
        now = datetime.utcnow()
        start_of_week = now - timedelta(days=now.weekday())
        previous_week_start = start_of_week - timedelta(days=7)

        current_week_count = self.session.query(func.count(Eventlog.id)).filter(Eventlog.time >= start_of_week).scalar()
        previous_week_count = self.session.query(func.count(Eventlog.id)).filter(Eventlog.time >= previous_week_start,
                                                                                 Eventlog.time < start_of_week).scalar()

        return {
            "current_week": current_week_count,
            "previous_week": previous_week_count,
            "change": (current_week_count - previous_week_count) / previous_week_count * 100 if previous_week_count else 0
        }

    def get_daily_stats(self):
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day)
        previous_day = start_of_day - timedelta(days=1)

        current_day_count = self.session.query(func.count(Eventlog.id)).filter(Eventlog.time >= start_of_day).scalar()
        previous_day_count = self.session.query(func.count(Eventlog.id)).filter(Eventlog.time >= previous_day,
                                                                                Eventlog.time < start_of_day).scalar()

        return {
            "current_day": current_day_count,
            "previous_day": previous_day_count,
            "change": (current_day_count - previous_day_count) / previous_day_count * 100 if previous_day_count else 0
        }

    # 월/주/일/시간대별 이상행동 건수
    def get_eventlog_monthly_stats(self):
        now = datetime.utcnow()
        start_year = datetime(now.year, 1, 1)
        all_months = get_all_months(now.year)
        result = self.session.query(
            func.date_format(Eventlog.time, '%Y-%m').label('period'),
            func.count(Eventlog.id).label('count')
        ).filter(Eventlog.time >= start_year).group_by('period').all()

        result_dict = {res.period: int(res.count) for res in result}

        stats = [{'period': month, 'count': result_dict.get(month, 0)} for month in all_months]
        return stats

    def get_eventlog_weekly_stats(self):
        now = datetime.utcnow()
        start_date = now - timedelta(weeks=5)
        all_weeks = get_all_weeks(start_date, 5)
        result = self.session.query(
            func.date_format(Eventlog.time, '%Y-%u').label('period'),
            func.count(Eventlog.id).label('count')
        ).filter(Eventlog.time >= start_date).group_by('period').all()

        result_dict = {res.period: int(res.count) for res in result}

        stats = [{'period': week, 'count': result_dict.get(week, 0)} for week in all_weeks]
        return stats

    def get_eventlog_daily_stats(self):
        now = datetime.utcnow()
        start_date = now - timedelta(days=6)
        all_days = get_all_days(start_date, 6)
        result = self.session.query(
            func.date_format(Eventlog.time, '%Y-%m-%d').label('period'),
            func.count(Eventlog.id).label('count')
        ).filter(Eventlog.time >= start_date).group_by('period').all()

        result_dict = {res.period: int(res.count) for res in result}

        stats = [{'period': day, 'count': result_dict.get(day, 0)} for day in all_days]
        return stats

    def get_eventlog_hourly_stats(self):
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, now.day)
        all_hours = get_all_hours()
        result = self.session.query(
            func.extract('hour', Eventlog.time).label('hour'),
            func.count(Eventlog.id).label('count')
        ).filter(Eventlog.time >= start_date).group_by('hour').all()

        result_dict = {str(int(res.hour)).zfill(2): int(res.count) for res in result}

        stats = [{'hour': hour, 'count': result_dict.get(hour, 0)} for hour in all_hours]
        return stats


