from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import asyncio

from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from database.connection import get_db
from database.orm import Frame, Anomaly

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 헤더를 허용
)

router = APIRouter(prefix="/stream")


class DummyModel:
    def predict(self, frame):
        return np.random.rand() > 0.5


model = DummyModel()

@router.websocket("/ws/cctv")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    print("**********  WebSocket connection accepted!! **********")

    try:
        while True:
            frame_bytes = await websocket.receive_bytes()
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                await websocket.send_json({"error": "Failed to decode the frame."})
                break

            # Save frame data and metadata to the database
            frame_record = save_frame_to_db(frame, db)

            if model.predict(frame):
                print("Abnormal behavior detected!")
                save_anomaly_to_db(frame_record.id, db)
                await websocket.send_json({"alert": "Abnormal behavior detected!"})

            await asyncio.sleep(0.042)

    except WebSocketDisconnect:
        print("**********  WebSocket disconnected  **********")

    finally:
        await websocket.close()


def generate_frames(cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if model.predict(frame):
            print("Abnormal behavior detected!")

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            break

        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
@router.get("/cctv")
async def stream_video():
    cap = cv2.VideoCapture(0)
    return StreamingResponse(generate_frames(cap), media_type="multipart/x-mixed-replace; boundary=frame")


# 동영상 업로드 엔드포인트 추가
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"/mnt/data/{file.filename}"

    # with open(video_path, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)

    # 동영상을 인공지능 서버로 전송 (예: 요청 코드 추가)
    # response = requests.post("http://ai-server/upload", files={"file": open(video_path, "rb")})

    return {"filename": file.filename, "message": "Video uploaded successfully"}