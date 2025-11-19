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
        orm_mode = True
