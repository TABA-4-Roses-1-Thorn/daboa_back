import asyncio
from typing import Optional

import aioredis
from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, RedirectResponse

from database.repository import UserRepository
from database.connection import get_db

from database.orm import User

from database.repository import oauth2_scheme, UserRepository

router = APIRouter(prefix="/setting")
SECRET_KEY = "3a3447a91a8abd0b04a08203682d896fb6f3816f0405de7aab56572a4b2b7975"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Redis 연결
redis = aioredis.from_url("redis://localhost:6379")

class TokenData(BaseModel):
    email: str
@router.post("/logout_screen")
def user_log_out_handler(response: Response):
    response.delete_cookie(key="session")
    return {"message": "Logged out successfully"}



# 현재 사용자 조회 함수
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    print('get current_user')
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Redis에서 토큰 조회 및 검증
    stored_token = await redis.get(email)
    if stored_token is None or stored_token.decode("utf-8") != token:
        raise credentials_exception

    user_repository = UserRepository(session=db)
    user = user_repository.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
@router.get("/setting_screen", response_class=JSONResponse)
async def read_settings(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/delete_account_screen", response_class=JSONResponse)
def delete_account(db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
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
        db: Session = Depends(get_db), user_id: int = Depends(get_current_user)
):
    if password and confirm_password and password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    updated_user = UserRepository(db).edit_user(user_id=user_id, username=username, email=email, password=password)
    return {"message": "User information updated successfully",
            "user": {"username": updated_user.username, "email": updated_user.email}}


