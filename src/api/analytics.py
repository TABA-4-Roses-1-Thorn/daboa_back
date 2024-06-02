from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.repository import AnalyticsRepository
from schema.response import AnalyticsResponse, StatsResponse, TimeStatsResponse

router = APIRouter(prefix="/analytics")

# 지난 월/주/일 대비 이상행동 건수
@router.get("/monthly", response_model=AnalyticsResponse)
def get_monthly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_monthly_stats()
    return stats

@router.get("/weekly", response_model=AnalyticsResponse)
def get_weekly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_weekly_stats()
    return stats

@router.get("/daily", response_model=AnalyticsResponse)
def get_daily_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_daily_stats()
    return stats

# 월/주/일/시간대별 이상행동 건수
@router.get("/eventlog_monthly", response_model=List[StatsResponse])
def get_eventlog_monthly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_monthly_stats()
    return [StatsResponse(period=period, count=count) for period, count in stats]

@router.get("/eventlog_weekly", response_model=List[StatsResponse])
def get_eventlog_weekly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_weekly_stats()
    return [StatsResponse(period=period, count=count) for period, count in stats]

@router.get("/eventlog_daily", response_model=List[StatsResponse])
def get_eventlog_daily_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_daily_stats()
    return [StatsResponse(period=period, count=count) for period, count in stats]

@router.get("/eventlog_hourly", response_model=List[TimeStatsResponse])
def get_eventlog_hourly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_hourly_stats()
    return [TimeStatsResponse(hour=hour, count=count) for hour, count in stats]