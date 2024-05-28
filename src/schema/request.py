from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LogInRequest(BaseModel):
    email: EmailStr
    password: str