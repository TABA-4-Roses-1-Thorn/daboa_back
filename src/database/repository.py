from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from pydantic import EmailStr

from database.connection import get_db
from database.orm import User, Setting

from schema.setting_schema import SettingUpdate,UserUpdate,SettingCreate


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
