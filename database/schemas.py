# schemas.py
from pydantic import BaseModel

class ChatSentimentLogCreate(BaseModel):
    question: str
    answer: str
    sentiment: str | None = None
    feedback: str | None = None

class ChatSentimentLogOut(BaseModel):
    id: int
    question: str
    answer: str
    sentiment: str | None
    feedback: str | None

    class Config:
        from_attributes = True


class UserDataCreate(BaseModel):
    email:str
    name:str
    password:str
    role:str

class UserDataOut(BaseModel):
    email:str
    name:str
    role:str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email:str
    password:str

class SaveChatRequest(BaseModel):
    question:str
    answer:str