from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
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
            email = email,
            password = hashed_password,
        )