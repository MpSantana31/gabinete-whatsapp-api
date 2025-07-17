from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.message import ChatHistory
from app.schemas.message import MessageCreate

class CRUDMessage:
    def create(self, db: Session, message: MessageCreate) -> ChatHistory:
        db_message = ChatHistory(
            session_id=message.session_id,
            sender=message.sender,
            content=message.content,
            message_metadata=message.metadata or {}
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_by_session(
        self, 
        db: Session, 
        session_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ChatHistory]:
        return (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_by_session(
        self,
        db: Session,
        session_id: str,
        limit: int = 10
    ) -> List[ChatHistory]:
        return (
            db.query(ChatHistory)
            .filter(ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_all(self, db: Session) -> List[ChatHistory]:
        return db.query(ChatHistory).all()

crud_message = CRUDMessage()