from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_attributes = True


class JWTResponse(BaseModel):
    access_token: str

class EventlogBase(BaseModel):
    date_time: datetime

class EventlogCreate(BaseModel):
    date_time: datetime = Field(..., example="2024-05-30T07:06:58.194000+00:00")

class EventlogResponse(BaseModel):
    id: int
    date_time: datetime

    class Config:
        orm_mode = True