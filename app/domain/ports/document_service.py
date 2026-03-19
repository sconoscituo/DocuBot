from abc import abstractmethod
from typing import Any, Dict, List

from app.domain.ports.base_service import AbstractService


class AbstractDocumentService(AbstractService):
    """DocuBot 도메인 서비스 포트."""

    @abstractmethod
    async def upload_document(self, user_id: str, file_content: bytes, filename: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """문서를 업로드하고 벡터 임베딩을 생성합니다."""
        ...

    @abstractmethod
    async def query_document(self, user_id: str, document_id: str, question: str) -> Dict[str, Any]:
        """문서에 대해 자연어 질의응답을 수행합니다."""
        ...

    @abstractmethod
    async def summarize(self, user_id: str, document_id: str, style: str = "brief") -> Dict[str, Any]:
        """문서를 지정된 스타일로 요약합니다."""
        ...

    async def health_check(self) -> Dict[str, Any]:
        return {"service": "DocumentService", "status": "ok"}
