import secrets
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.utils.auth import get_current_user
from app.services.extractor import extract_text_from_pdf, extract_text_from_url
from app.config import config

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: int
    title: str
    source_type: str
    source_url: str | None
    share_token: str | None
    created_at: datetime

    class Config:
        from_attributes = True


async def check_doc_limit(user: User, db: AsyncSession):
    if user.is_premium:
        return
    result = await db.execute(select(Document).where(Document.user_id == user.id))
    docs = result.scalars().all()
    if len(docs) >= config.FREE_DOCUMENTS_LIMIT:
        raise HTTPException(status_code=403, detail=f"Free plan allows max {config.FREE_DOCUMENTS_LIMIT} documents")


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_doc_limit(current_user, db)
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()
    if len(file_bytes) > config.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large (max {config.MAX_FILE_SIZE_MB}MB)")

    content_text = await extract_text_from_pdf(file_bytes)
    if not content_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(config.UPLOAD_DIR, f"{secrets.token_hex(8)}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    doc = Document(
        user_id=current_user.id,
        title=title,
        content_text=content_text,
        source_type="pdf",
        file_path=file_path,
        share_token=secrets.token_urlsafe(16),
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.post("/crawl", response_model=DocumentResponse, status_code=201)
async def crawl_url(
    title: str = Form(...),
    url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_doc_limit(current_user, db)
    try:
        content_text = await extract_text_from_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to crawl URL: {str(e)}")

    if not content_text.strip():
        raise HTTPException(status_code=400, detail="No text content found at URL")

    doc = Document(
        user_id=current_user.id,
        title=title,
        content_text=content_text,
        source_type="url",
        source_url=url,
        share_token=secrets.token_urlsafe(16),
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)
    return doc


@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.user_id == current_user.id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
