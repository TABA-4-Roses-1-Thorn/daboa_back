from pydantic import BaseModel

class AiMessageCreate(BaseModel):
    content: str

class AiMessageUpdate(BaseModel):
    content: str

class AiMessageSchema(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True