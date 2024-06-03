from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from database.connection import get_db
from database.repository import UserRepository

import secrets

def generate_secret_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

SECRET_KEY = generate_secret_key()
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_jwt(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_jwt(token)
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = get_db()
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    return user.id
