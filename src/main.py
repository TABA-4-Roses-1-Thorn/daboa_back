from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api import user, realstream, setting, eventlog, ai_message, TTS

# 데이터베이스 테이블 생성
#Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",  # Flutter 앱을 실행하는 도메인 추가
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://your-frontend-domain",  # 필요한 경우 다른 도메인 추가
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션 설정 -> 로그인 시에 session id 획득 --> 로그아웃 기능까지 이어지도록 구성
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.include_router(user.router)
@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    session_id = request.cookies.get("session")
    if session_id:
        request.state.user_id = int(session_id)
    else:
        request.state.user_id = None
    response = await call_next(request)
    return response

app.include_router(realstream.router)
app.include_router(setting.router)
app.include_router(ai_message.router)
app.include_router(eventlog.router)
app.include_router(TTS.router)

@app.get("/")
def haelth_check_handler():
    return {"Hello": "World"}