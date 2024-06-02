from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse

from database.repository import UserRepository
from database.connection import get_db
from schema.setting_schema import UserUpdate

router = APIRouter(prefix="/setting")

@router.post("/logout_screen")
def user_log_out_handler(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Logged out successfully"}

def get_current_user_id(request: Request):
    if request.state.user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user_id


# 회원정보 표시해주는 get 문서
@router.get("/setting_screen", response_class=JSONResponse)
def read_settings(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = UserRepository(db).get_user(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email}

@router.delete("/delete_account_screen", response_class=JSONResponse)
def delete_account(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    try:
        UserRepository(db).delete_user(user_id=user_id)
        return {"message": "Account deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
#
# @router.get("/edit", response_class=JSONResponse)
# def edit_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
#     user = UserRepository.get_user(db, user_id=user_id)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"username": user.username, "email": user.email}

@router.patch("/user_info_edit_screen", response_class=JSONResponse)
def update_user(
        username: str = None, email: str = None, password: str = None, confirm_password: str = None,
        db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    if password and confirm_password and password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    updated_user = UserRepository(db).edit_user(user_id=user_id, username=username, email=email, password=password)
    return {"message": "User information updated successfully",
            "user": {"username": updated_user.username, "email": updated_user.email}}


