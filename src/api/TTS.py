import os

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from gtts import gTTS
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from database.connection import get_db
from database.orm import AiMessage

router = APIRouter(prefix="/tts")


def save_tts_audio(text: str, file_path: str):
    tts = gTTS(text=text, lang='ko')
    tts.save(file_path)


@router.post("/{message_id}")
async def text_to_speech(message_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ai_message = db.query(AiMessage).filter(AiMessage.id == message_id).first()
    if not ai_message:
        raise HTTPException(status_code=404, detail="Message not found")

    file_path = f"../TTS_audio/tts_audio_{message_id}.mp3"
    background_tasks.add_task(save_tts_audio, ai_message.content, file_path)

    return {"message": "TTS processing started", "file_path": file_path}
@router.get("/{text}", response_class = FileResponse)
async def get_tts_audio(message_id: int):
    file_path = f"../TTS_audio/tts_audio_{message_id}.mp3"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type='audio/mpeg', filename=f'tts_audio_{message_id}.mp3')