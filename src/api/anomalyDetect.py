import json
from datetime import datetime, timedelta

from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
import requests
import os

from sqlalchemy.orm import Session

from database.connection import get_db

from database.orm import Eventlog

router = APIRouter(prefix="/stream")
# Colab 서버 URL (ngrok URL)
COLAB_SERVER_URL = "http://romantic-goshawk-comic.ngrok-free.app/process-video/"

# 저장할 디렉토리 경로
SAVE_DIR = "../anomaly_detect_json"
os.makedirs(SAVE_DIR, exist_ok=True)  # 디렉토리가 없으면 생성

@router.post("/upload/")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        files = {"file": (file.filename, file.file, file.content_type)}
        response = requests.post(COLAB_SERVER_URL, files=files, verify=False)
        print(f"Request sent to {COLAB_SERVER_URL} with status code {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            # Colab 서버로부터 JSON 응답을 받음
            json_response = response.json()
            # 시작 시간과 끝 시간의 차이가 3초 이상인 항목만 필터링
            filtered_anomaly_times = [interval for interval in json_response["anomaly_times"] if interval[1] - interval[0] >= 3.0]
            filtered_response = {"anomaly_times": filtered_anomaly_times}
            # JSON 파일 저장 경로 설정
            json_filename = os.path.splitext(file.filename)[0] + "_anomaly.json"
            json_save_path = os.path.join(SAVE_DIR, json_filename)
            # JSON 파일로 저장
            with open(json_save_path, "w") as json_file:
                json.dump(filtered_response, json_file)

            # 데이터베이스에 삽입
            today = datetime.today()
            for start, end in filtered_anomaly_times:
                start_time = today + timedelta(seconds=start)
                video_link = f"{file.filename}?start={int(start)}"
                db_event = Eventlog(type="이상행동", time=start_time, state=False, video=video_link)
                db.add(db_event)
            db.commit()

            return {"detail": "File processed successfully", "file_path": json_save_path, "anomaly_times": filtered_response}
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)