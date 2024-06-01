from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from database.orm import User, EventlogSchedule
from database.repository import UserRepository, EventlogRepository
from schema.request import SignUpRequest, LogInRequest, EventlogCreate
from schema.response import UserSchema, JWTResponse, EventlogScheduleResponse, EventlogScheduleCreate, EventlogResponse
from service.user import UserService
from database.connection import get_db

router = APIRouter(prefix="/eventlog")

@router.post("/eventlog_schedule", response_model=EventlogScheduleResponse)
def eventlog_schedule_handler(
        schedule: EventlogScheduleCreate, db: Session = Depends(get_db)
):
    eventlog_schedule_repository = EventlogRepository(db)
    eventlog_schedule = eventlog_schedule_repository.create_date_time(date_time=schedule.date_time)
    return eventlog_schedule

@router.post("/", response_model=EventlogResponse)
def create_eventlog(
        eventlog: EventlogCreate, db: Session = Depends(get_db)
):
    repository = EventlogRepository(db)
    return repository.create_eventlog(eventlog)

@router.get("/", response_model=List[EventlogResponse])
def read_eventlog(
        skip: int = 0,
        limit: int = 10,
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        db: Session = Depends(get_db)):
    repository = EventlogRepository(db)
    return repository.get_eventlog(skip=skip, limit=limit, start_date=start_date, end_date=end_date)

@router.get("/all", response_model=List[EventlogResponse])
def read_all_eventlogs(db: Session = Depends(get_db)):
    repository = EventlogRepository(db)
    return repository.get_all_eventlogs()