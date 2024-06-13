from fastapi import FastAPI, File, UploadFile, APIRouter, HTTPException
import requests
import os

router = APIRouter(prefix="/stream")
# Colab 서버 URL (ngrok URL)
COLAB_SERVER_URL = "http://romantic-goshawk-comic.ngrok-free.app/process-video/"

# 저장할 디렉토리 경로
SAVE_DIR = "../csv"


@router.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        files = {"file": (file.filename, file.file, file.content_type)}
        response = requests.post(COLAB_SERVER_URL, files=files, verify=False)
        print(f"Request sent to {COLAB_SERVER_URL} with status code {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            # 파일 저장 경로 설정
            save_path= os.path.join(SAVE_DIR, "output.csv")
            # CSV 파일 저장
            with open(save_path, "wb") as f:
                f.write(response.content)
            return {"detail": "File saved successfully", "file_path": save_path}
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
