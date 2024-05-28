from datetime import datetime, timedelta
from pydantic import EmailStr

import bcrypt
from jose import jwt


class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "3a3447a91a8abd0b04a08203682d896fb6f3816f0405de7aab56572a4b2b7975"
    jwt_algorithm: str = "HS256"

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

    def create_jwt(self, email: EmailStr) -> str:
        return jwt.encode(
            {
                "sub": email,
                "exp": datetime.now() + timedelta(days=1),  # 하루까지 토큰 유효
            },
            self.secret_key,
            algorithm=self.jwt_algorithm,
        )

    def decode_jwt(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token, self.secret_key, algorithms=[self.jwt_algorithm]
        )
        return payload["sub"]