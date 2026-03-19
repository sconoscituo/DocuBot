from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.payment import Payment
from app.models.user import User


async def create_payment(db: AsyncSession, user_id: int, amount: float, plan: str, transaction_id: str = None) -> Payment:
    payment = Payment(
        user_id=user_id,
        amount=amount,
        plan=plan,
        status="completed",
        transaction_id=transaction_id,
    )
    db.add(payment)
    await db.flush()
    await db.refresh(payment)
    return payment


async def upgrade_to_premium(db: AsyncSession, user_id: int) -> User:
    await db.execute(update(User).where(User.id == user_id).values(is_premium=True))
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one()


async def get_payment_history(db: AsyncSession, user_id: int) -> list[Payment]:
    result = await db.execute(select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc()))
    return result.scalars().all()
