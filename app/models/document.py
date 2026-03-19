from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content_text = Column(Text, nullable=True)
    source_type = Column(String, nullable=False)  # "pdf" or "url"
    source_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    share_token = Column(String, unique=True, index=True, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of extracted topics/tags
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
