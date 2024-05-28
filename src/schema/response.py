from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True
        from_attributes = True


class JWTResponse(BaseModel):
    access_token: str