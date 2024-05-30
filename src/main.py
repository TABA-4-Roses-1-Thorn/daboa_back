from fastapi import FastAPI

from api import user, realstream, setting, eventlog
# 데이터베이스 테이블 생성
#Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(realstream.router)
app.include_router(setting.router)
app.include_router(eventlog.router)

@app.get("/")
def haelth_check_handler():
    return {"Hello": "World"}