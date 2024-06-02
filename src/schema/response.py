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

class EventlogScheduleBase(BaseModel):
    date_time: datetime

class EventlogScheduleCreate(BaseModel):
    date_time: datetime = Field(..., example="2024-05-30T07:06:58.194000+00:00")

class EventlogScheduleResponse(BaseModel):
    id: int
    date_time: datetime

    class Config:
        orm_mode = True

class EventlogResponse(BaseModel):
    id: int
    type: str
    time: datetime
    state: bool
    video: str

    class Config:
        orm_mode = True

class AnalyticsResponse(BaseModel):
    current_month: int
    previous_month: int
    change: float

    class Config:
        orm_mode = True

class StatsResponse(BaseModel):
    period: str
    count: int

class TimeStatsResponse(BaseModel):
    hour: int
    count: int