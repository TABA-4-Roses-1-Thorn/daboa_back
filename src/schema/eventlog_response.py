from pydantic import BaseModel
from datetime import datetime

class EventlogResponse(BaseModel):
    id: int
    type: str
    time: datetime
    state: bool
    video: str

    class Config:
        orm_mode = True

class EventlogCreate(BaseModel):
    date_time: datetime
