from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str
    confirm_password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class SettingBase(BaseModel):
    ai_message: str

class SettingCreate(SettingBase):
    pass

class SettingUpdate(SettingBase):
    pass

class Setting(SettingBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
