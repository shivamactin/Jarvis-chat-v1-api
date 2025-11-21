# models.py
from sqlalchemy import Column, Integer, Text
from database.database import Base

class ChatSentimentLog(Base):
    __tablename__ = "sentiment"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sentiment = Column(Text)
    feedback = Column(Text)


class UserData(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(Text,nullable=False)
    password = Column(Text,nullable=False)
    role = Column(Text,nullable=False)
    name = Column(Text,nullable=True)

class SaveChatResponse(Base):
    __tablename__ = "chats"

    id=Column(Integer,primary_key=True,index=True)
    question=Column(Text,nullable=False)
    answer=Column(Text,nullable=False)