import json
from datetime import datetime, timedelta
from urllib.parse import quote

import boto3
import fastapi
from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException, Depends
import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from sqlalchemy.orm import Session

from database.connection import get_db

from database.orm import Eventlog
import pytz

# 한국 표준시 타임존
kst = pytz.timezone('Asia/Seoul')

router = APIRouter(prefix="/stream")
# Colab 서버 URL (ngrok URL)
COLAB_SERVER_URL = "http://romantic-goshawk-comic.ngrok-free.app/process-video/"

# json 파일 저장
SAVE_DIR = "../anomaly_detect_json"

# AWS S3 설정
from dotenv import load_dotenv

# .env 파일의 내용을 로드합니다.
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = 'daboa-s3'
AWS_REGION_NAME = 'ap-northeast-2'

s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                         region_name=AWS_REGION_NAME)

# S3에 파일 업로드 함수
def upload_to_s3(file: UploadFile, bucket: str, key: str):
    try:
        # 파일 포인터를 처음으로 재설정
        file.file.seek(0)
        s3_client.upload_fileobj(file.file, bucket, key, ExtraArgs={
            'ContentType': 'video/mp4',
            'ACL': 'bucket-owner-full-control'
        })
        return f"https://{bucket}.s3.{AWS_REGION_NAME}.amazonaws.com/{key}"
    except Exception as e:
        print(f"Exception occurred during S3 upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")

@router.post("/upload")
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # S3에 파일 업로드
        s3_url = upload_to_s3(file, AWS_S3_BUCKET_NAME, file.filename)

        # Colab 서버로 비디오 처리 요청
        file.file.seek(0)  # 파일 포인터를 처음으로 재설정
        files = {'file': (file.filename, file.file, file.content_type)}
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


            if filtered_anomaly_times:
                last_start, last_end = filtered_anomaly_times[-1]
                start_time = datetime.now(kst)
                video_link = f"{s3_url}#t={int(last_start)}"
                db_event = Eventlog(type="이상행동", time=start_time, state=False, video=quote(video_link, safe=':/#?&='))
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

