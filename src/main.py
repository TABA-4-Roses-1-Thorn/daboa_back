from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from api import user, realstream, setting, eventlog, ai_message, TTS, analytics, anomalyDetect

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    try:
        session_id = request.cookies.get("session")
        if session_id:
            request.state.user_id = int(session_id)
        else:
            request.state.user_id = None
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred"}
        )

app.include_router(user.router)
app.include_router(realstream.router)
app.include_router(setting.router)
app.include_router(ai_message.router)
app.include_router(eventlog.router)
app.include_router(TTS.router)
app.include_router(analytics.router)
app.include_router(anomalyDetect.router)

@app.get("/")
<<<<<<< HEAD
def haelth_check_handler():
=======
def health_check_handler():
>>>>>>> 8dcfc5854fdc7f8d40123e025d193839afa4fb7e
    return {"Hello": "World"}
