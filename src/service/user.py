from datetime import datetime, timedelta
from http.client import HTTPException

import aioredis
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

import bcrypt
from jose import jwt


class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "3a3447a91a8abd0b04a08203682d896fb6f3816f0405de7aab56572a4b2b7975"
    jwt_algorithm: str = "HS256"

    # Redis 연결
    redis = aioredis.from_url("redis://localhost")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding),
            salt=bcrypt.gensalt(),
        )
        return hashed_password.decode(self.encoding)

    def verify_password(
            self, plain_password: str, hashed_password: str
    ) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding),
        )

    # JWT 생성 및 세션 저장 함수
    async def create_jwt(self, email: EmailStr) -> str:
        to_encode = {
            "sub": email,
            "exp": datetime.utcnow() + timedelta(days=1)  # 하루 동안 유효
        }
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.jwt_algorithm)

        # Redis에 토큰 저장 (유효 기간과 동일하게 설정)
        await self.redis.set(email, token, ex=86400)  # 86400초 = 1일

        return token

    def decode_jwt(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token, self.secret_key, algorithms=[self.jwt_algorithm]
        )
        return payload["sub"]

    def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")