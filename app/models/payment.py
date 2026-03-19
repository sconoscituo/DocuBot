from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="KRW")
    plan = Column(String, nullable=False)
    status = Column(String, default="pending")
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
