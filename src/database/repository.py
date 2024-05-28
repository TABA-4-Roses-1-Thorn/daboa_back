from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from pydantic import EmailStr

from database.connection import get_db
from database.orm import User

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