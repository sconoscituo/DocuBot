from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.chat import Chat
from app.utils.auth import get_current_user
from app.services.qa_engine import answer_question, generate_document_summary, suggest_questions
from app.config import config

router = APIRouter(prefix="/api/chats", tags=["chats"])


class QuestionRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    id: int
    document_id: int
    question: str
    answer: str | None
    created_at: datetime

    class Config:
        from_attributes = True


async def get_document_or_404(doc_id: int, db: AsyncSession) -> Document:
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


async def check_question_limit(user: User, db: AsyncSession):
    if user.is_premium:
        return
    if user.monthly_question_count >= config.FREE_QUESTIONS_LIMIT:
        raise HTTPException(status_code=403, detail=f"Free plan allows {config.FREE_QUESTIONS_LIMIT} questions/month")


@router.post("/{doc_id}/ask", response_model=ChatResponse)
async def ask_question(
    doc_id: int,
    body: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    await check_question_limit(current_user, db)

    answer = await answer_question(doc.content_text or "", body.question)
    chat = Chat(document_id=doc.id, user_id=current_user.id, question=body.question, answer=answer)
    db.add(chat)

    await db.execute(
        update(User).where(User.id == current_user.id).values(monthly_question_count=current_user.monthly_question_count + 1)
    )
    await db.flush()
    await db.refresh(chat)
    return chat


@router.post("/shared/{share_token}/ask", response_model=ChatResponse)
async def ask_shared(share_token: str, body: QuestionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.share_token == share_token))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Shared document not found")

    answer = await answer_question(doc.content_text or "", body.question)
    chat = Chat(document_id=doc.id, question=body.question, answer=answer)
    db.add(chat)
    await db.flush()
    await db.refresh(chat)
    return chat


@router.get("/{doc_id}/history", response_model=list[ChatResponse])
async def chat_history(doc_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Document not found")
    result = await db.execute(
        select(Chat).where(Chat.document_id == doc_id).order_by(Chat.created_at.desc()).limit(50)
    )
    return result.scalars().all()


@router.get("/{doc_id}/summary")
async def get_summary(doc_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    summary = await generate_document_summary(doc.content_text or "")
    return {"summary": summary}


@router.get("/{doc_id}/suggest")
async def get_suggestions(doc_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    questions = await suggest_questions(doc.content_text or "")
    return {"questions": questions}
