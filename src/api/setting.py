from fastapi import APIRouter, FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse

from database.orm import Setting
from database.repository import UserRepository
from database.connection import get_db
from schema.setting_schema import UserUpdate

router = APIRouter(prefix="/setting")

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

 #예제용 사용자 ID 함수
def get_current_user_id():
     # 실제로는 OAuth2, JWT 등을 통해 인증된 사용자 ID를 가져와야 합니다.
     return 1


@router.get("/settings", response_class=JSONResponse)
def read_settings(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = UserRepository.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email}

@router.get("/logout", response_class=JSONResponse)
def logout_confirm():
    return {"message": "Do you really want to log out?"}

@router.get("/delete", response_class=JSONResponse)
def delete_confirm():
    return {"message": "Do you really want to delete your account?"}

@router.post("/delete", response_class=JSONResponse)
def delete_account(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = UserRepository.get_user(db, user_id=user_id)
    if user:
        db.delete(user)
        db.commit()
        return {"message": "Account deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/edit", response_class=JSONResponse)
def edit_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = UserRepository.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email}

@router.post("/edit", response_class=JSONResponse)
def update_user(
    username: str, email: str, password: str, confirm_password: str,
    db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    user_update = UserUpdate(username=username, email=email, password=password, confirm_password=confirm_password)
    updated_user = UserRepository.update_user(db, user_id=user_id, user=user_update)
    return {"message": "User information updated successfully"}

@router.get("/features", response_class=JSONResponse)
def read_features():
    return {"message": "Features page"}

@router.get("/ai-message", response_class=JSONResponse)
def read_ai_message(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    settings = db.query(Setting.Setting).filter(Setting.user_id == user_id).all()
    return {"settings": settings}

@router.post("/ai-message", response_class=JSONResponse)
def update_ai_message(ai_message: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    setting = UserRepository.SettingCreate(ai_message=ai_message)
    UserRepository.create_setting(db, setting=setting, user_id=user_id)
    return {"message": "AI message setting updated successfully"}

@router.get("/others", response_class=JSONResponse)
def read_others():
    return {"message": "Others page"}
