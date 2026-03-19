from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.payment import create_payment, upgrade_to_premium, get_payment_history

router = APIRouter(prefix="/api/payments", tags=["payments"])


class PaymentCreate(BaseModel):
    plan: str
    transaction_id: str | None = None


PLAN_PRICES = {"monthly": 9900.0, "yearly": 99000.0}


@router.post("/upgrade")
async def upgrade(data: PaymentCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    amount = PLAN_PRICES.get(data.plan, 9900.0)
    await create_payment(db, current_user.id, amount, data.plan, data.transaction_id)
    user = await upgrade_to_premium(db, current_user.id)
    return {"message": "Upgraded to premium", "is_premium": user.is_premium}


@router.get("/history")
async def payment_history(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    payments = await get_payment_history(db, current_user.id)
    return payments
