from pydantic import BaseModel, EmailStr
from datetime import datetime


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LogInRequest(BaseModel):
    email: EmailStr
    password: str

class EventlogCreate(BaseModel):
    type: str
    time: datetime
    state: bool = False
    video: str