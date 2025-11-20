# crud.py
from sqlalchemy.orm import Session
from database.models import ChatSentimentLog,UserData
from database.schemas import ChatSentimentLogCreate,UserDataCreate

def create_entry(db: Session, data: ChatSentimentLogCreate):
    entry = ChatSentimentLog(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def get_latest(db: Session):
    return db.query(ChatSentimentLog).order_by(ChatSentimentLog.id.desc()).first()

def list_all(db: Session):
    return db.query(ChatSentimentLog).all()

def update_feedback(db: Session, entry_id: int, feedback: str):
    record = db.query(ChatSentimentLog).filter(ChatSentimentLog.id == entry_id).first()
    if record:
        record.feedback = feedback
        db.commit()
        db.refresh(record)
    return record

def create_user_data_entry(db:Session,data:UserDataCreate):
    entry = UserData(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

