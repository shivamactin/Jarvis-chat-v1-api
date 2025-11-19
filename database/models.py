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