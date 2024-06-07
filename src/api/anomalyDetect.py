from http.client import HTTPException

from fastapi import FastAPI, File, UploadFile, APIRouter
from fastapi.responses import FileResponse
import uvicorn
import requests
import shutil

router = APIRouter(prefix="/anomalyDetect")
# Colab 서버 URL (ngrok URL)
COLAB_SERVER_URL = "https://a7e1-34-173-73-198.ngrok-free.app/process-video/"

@router.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        # 동영상 파일을 임시로 저장
        with open("temp_video.mp4", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Colab 서버로 동영상 전송
        with open('temp_video.mp4', 'rb') as video_file:
            files = {'file': ('temp_video.mp4', video_file, 'video/mp4')}
            response = requests.post(COLAB_SERVER_URL, files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to process video on Colab server")

        # Colab 서버로부터 CSV 파일 다운로드
        with open("output.csv", "wb") as f:
            f.write(response.content)

        return FileResponse("output.csv", media_type='text/csv', filename="output.csv")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
