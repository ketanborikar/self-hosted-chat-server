from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Message, SessionLocal

router = APIRouter(prefix="/chat")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send")
def send_message(sender_id: int, receiver_id: int, content: str, db: Session = Depends(get_db)):
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    db.commit()
    return {"message": "Message sent"}

@router.get("/history/{user_id}")
def get_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter((Message.receiver_id == user_id) | (Message.sender_id == user_id)).order_by(Message.timestamp).all()
    return messages
