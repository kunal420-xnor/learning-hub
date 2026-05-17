from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://localhost/learning_hub"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255))
    user_message = Column(Text)
    ai_reply = Column(Text)
    char_count = Column(Integer)
    passed_validation = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    print("PostgreSQL database initialized")

def save_message(session_id, user_message, ai_reply, passed_validation):
    db = SessionLocal()
    try:
        conversation = Conversation(
            session_id=session_id,
            user_message=user_message,
            ai_reply=ai_reply,
            char_count=len(ai_reply),
            passed_validation=passed_validation
        )
        db.add(conversation)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"DB error: {e}")
    finally:
        db.close()

def get_all_conversations():
    db = SessionLocal()
    try:
        return db.query(Conversation).order_by(Conversation.timestamp.desc()).all()
    finally:
        db.close()

def get_stats():
    db = SessionLocal()
    try:
        total = db.query(Conversation).count()
        passed = db.query(Conversation).filter(Conversation.passed_validation == True).count()
        return {"total": total, "passed": passed, "failed": total - passed}
    finally:
        db.close()
