from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
