from datetime import datetime, timedelta
import calendar

def get_all_months(year):
    return [f"{year}-{str(month).zfill(2)}" for month in range(1, 13)]

def get_all_weeks(start_date, weeks):
    return [(start_date + timedelta(weeks=i)).strftime("%Y-%U") for i in range(weeks)]

def get_all_days(start_date, days):
    return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def get_all_hours():
    return [str(hour).zfill(2) for hour in range(24)]
