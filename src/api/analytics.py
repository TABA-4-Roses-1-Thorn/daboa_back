from datetime import datetime

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.repository import AnalyticsRepository
from schema.response import AnalyticsResponse, StatsResponse, TimeStatsResponse, MonthlyStatsResponse, WeeklyStatsResponse, DailyStatsResponse

router = APIRouter(prefix="/analytics")

# 지난 월/주/일 대비 이상행동 건수
@router.get("/monthly", response_model=MonthlyStatsResponse)
def get_monthly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_monthly_stats()
    stats['change'] = round(stats['change'], 2)
    return stats

@router.get("/weekly", response_model=WeeklyStatsResponse)
def get_weekly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_weekly_stats()
    stats['change'] = round(stats['change'], 2)
    return stats

@router.get("/daily", response_model=DailyStatsResponse)
def get_daily_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_daily_stats()
    stats['change'] = round(stats['change'], 2)
    return stats

# 월/주/일/시간대별 이상행동 건수
@router.get("/eventlog_monthly", response_model=List[StatsResponse])
def get_eventlog_monthly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_monthly_stats()
    # Extracting only the month from the period
    return [StatsResponse(period=stat['period'].split('-')[1], count=stat['count']) for stat in stats]


@router.get("/eventlog_weekly", response_model=List[StatsResponse])
def get_eventlog_weekly_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_weekly_stats()

    # 현재 날짜를 기준으로 몇 주 전인지를 계산
    current_week = datetime.utcnow().isocalendar()[1]
    current_year = datetime.utcnow().isocalendar()[0]
    current_week_period = f"{current_year}-{current_week:02}"

    def calculate_weeks_ago(target_period: str) -> str:
        target_year, target_week = map(int, target_period.split('-'))
        delta_weeks = (current_year - target_year) * 52 + (current_week - target_week)
        if delta_weeks == 0:
            return "이번 주"
        else:
            return f"{delta_weeks-1}주 전"

    formatted_stats = [
        StatsResponse(
            period=calculate_weeks_ago(stat['period']),
            count=stat['count']
        ) for stat in stats
    ]

    return formatted_stats

@router.get("/eventlog_daily", response_model=List[StatsResponse])
def get_eventlog_daily_stats(db: Session = Depends(get_db)):
    repository = AnalyticsRepository(db)
    stats = repository.get_eventlog_daily_stats()
    return [StatsResponse(period=stat['period'], count=stat['count']) for stat in stats]

# @router.get("/eventlog_hourly", response_model=List[TimeStatsResponse])
# def get_eventlog_hourly_stats(db: Session = Depends(get_db)):
#     repository = AnalyticsRepository(db)
#     stats = repository.get_eventlog_hourly_stats()
#     return [TimeStatsResponse(hour=stat['hour'], count=stat['count']) for stat in stats]