from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import FileResponse
import uvicorn
import requests
import shutil

router = APIRouter(prefix="/anomalyDetect")

# Colab 서버 URL (ngrok URL)
COLAB_SERVER_URL = "http://127.0.0.1:5000/process-video/"

@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    with open("temp_video.mp4", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Colab 서버로 영상 전송
    files = {'file': ('temp_video.mp4', open('temp_video.mp4', 'rb'), 'video/mp4')}
    response = requests.post(COLAB_SERVER_URL, files=files)

    # Colab 서버로부터 CSV 파일 다운로드
    with open("output.csv", "wb") as f:
        f.write(response.content)

    return FileResponse("output.csv", media_type='text/csv', filename="output.csv")
