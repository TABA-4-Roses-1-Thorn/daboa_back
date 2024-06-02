from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from database.orm import AiMessage
from schema.ai_message_schema import AiMessageCreate, AiMessageUpdate, AiMessageSchema

router = APIRouter(prefix="/setting_ai_message")

# 모든 AI 메시지 조회
@router.get("/ai_audio_ment_settings_screen", response_model=List[AiMessageSchema])
def read_ai_messages(db: Session = Depends(get_db)):
    ai_messages = db.query(AiMessage).all()
    return ai_messages

# 새로운 AI 메시지 추가
@router.post("/ai_audio_ment_settings_screen", response_model=AiMessageSchema)
def create_ai_message(ai_message: AiMessageCreate, db: Session = Depends(get_db)):
    db_ai_message = AiMessage(content=ai_message.content)
    db.add(db_ai_message)
    db.commit()
    db.refresh(db_ai_message)
    return db_ai_message

# 기존 AI 메시지 수정
@router.patch("/ai_audio_ment_settings_screen/{ai_message_id}", response_model=AiMessageSchema)
def update_ai_message(ai_message_id: int, ai_message: AiMessageUpdate, db: Session = Depends(get_db)):
    db_ai_message = db.query(AiMessage).filter(AiMessage.id == ai_message_id).first()
    if db_ai_message is None:
        raise HTTPException(status_code=404, detail="AI Message not found")
    db_ai_message.content = ai_message.content
    db.commit()
    db.refresh(db_ai_message)
    return db_ai_message

# AI 메시지 삭제
@router.delete("/ai_audio_ment_settings_screen/{ai_message_id}", response_class=Response)
def delete_ai_message(ai_message_id: int, db: Session = Depends(get_db)):
    db_ai_message = db.query(AiMessage).filter(AiMessage.id == ai_message_id).first()
    if db_ai_message is None:
        raise HTTPException(status_code=404, detail="AI Message not found")
    db.delete(db_ai_message)
    db.commit()
    return Response(status_code=204)
