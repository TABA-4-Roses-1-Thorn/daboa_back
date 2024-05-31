from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from database.orm import User, EventlogSchedule
from database.repository import UserRepository, EventlogRepository
from schema.request import SignUpRequest, LogInRequest
from schema.response import UserSchema, JWTResponse, EventlogResponse, EventlogCreate
from service.user import UserService
from database.connection import get_db

router = APIRouter(prefix="/eventlog")

@router.post("/video_schedule", response_model=EventlogResponse)
def eventlog_schedule_handler(
        schedule: EventlogCreate, db: Session = Depends(get_db)
):
    eventlog_schedule_repository = EventlogRepository(db)
    eventlog_schedule = eventlog_schedule_repository.create_date_time(date_time=schedule.date_time)
    return eventlog_schedule