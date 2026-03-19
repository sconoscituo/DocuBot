from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.services.document_search import DocumentSearchService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["search"])

search_service = DocumentSearchService()


@router.get("/search")
async def semantic_search(
    q: str = Query(..., min_length=1, description="검색어"),
    top_k: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """전체 문서 시맨틱(키워드) 검색"""
    result = await db.execute(
        select(Document).where(Document.user_id == current_user.id)
    )
    documents = result.scalars().all()

    if not documents:
        return {"query": q, "results": [], "total": 0}

    matched = await search_service.semantic_search(q, documents, top_k=top_k)

    return {
        "query": q,
        "results": [
            {
                "id": doc.id,
                "title": doc.title,
                "source_type": doc.source_type,
                "tags": doc.tags if hasattr(doc, "tags") else None,
                "created_at": doc.created_at,
            }
            for doc in matched
        ],
        "total": len(matched),
    }


@router.get("/documents/{document_id}/similar")
async def get_similar_documents(
    document_id: int,
    top_k: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """유사 문서 추천"""
    target_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    target_doc = target_result.scalar_one_or_none()
    if not target_doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    all_result = await db.execute(
        select(Document).where(Document.user_id == current_user.id)
    )
    all_documents = all_result.scalars().all()

    similar = await search_service.find_similar_documents(target_doc, all_documents, top_k=top_k)

    return {
        "document_id": document_id,
        "similar_documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "source_type": doc.source_type,
                "created_at": doc.created_at,
            }
            for doc in similar
        ],
        "total": len(similar),
    }


@router.get("/documents/{document_id}/topics")
async def get_document_topics(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """문서 핵심 토픽 추출"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    if not doc.content_text:
        raise HTTPException(status_code=400, detail="문서 텍스트가 없습니다.")

    topics = await search_service.extract_key_topics(doc.content_text)

    # tags 필드가 있으면 저장
    if hasattr(doc, "tags"):
        import json
        doc.tags = json.dumps(topics, ensure_ascii=False)
        await db.commit()

    return {
        "document_id": document_id,
        "title": doc.title,
        "topics": topics,
    }
