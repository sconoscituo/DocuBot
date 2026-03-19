import math
import re
import json
import google.generativeai as genai
from app.config import config


def _init_genai():
    if config.GEMINI_API_KEY:
        genai.configure(api_key=config.GEMINI_API_KEY)


def _tokenize(text: str) -> list[str]:
    """텍스트를 소문자 토큰으로 분리"""
    return re.findall(r"[가-힣a-zA-Z0-9]+", text.lower())


def _tf_idf_score(query_tokens: list[str], doc_text: str, all_docs_texts: list[str]) -> float:
    """간단한 TF-IDF 기반 유사도 점수"""
    doc_tokens = _tokenize(doc_text)
    if not doc_tokens:
        return 0.0

    doc_freq: dict[str, int] = {}
    for t in doc_tokens:
        doc_freq[t] = doc_freq.get(t, 0) + 1

    total_docs = len(all_docs_texts)
    score = 0.0
    for token in query_tokens:
        tf = doc_freq.get(token, 0) / len(doc_tokens)
        # document frequency across corpus
        df = sum(1 for dt in all_docs_texts if token in _tokenize(dt))
        idf = math.log((total_docs + 1) / (df + 1)) + 1
        score += tf * idf

    return score


class DocumentSearchService:
    async def semantic_search(
        self,
        query: str,
        documents: list,
        top_k: int = 5,
    ) -> list:
        """키워드 기반 TF-IDF 유사도 검색 (Gemini embed_content 미지원 환경 대비)"""
        if not documents:
            return []

        query_tokens = _tokenize(query)
        all_texts = [
            f"{doc.title} {doc.content_text or ''}" for doc in documents
        ]

        scored = []
        for doc, doc_text in zip(documents, all_texts):
            score = _tf_idf_score(query_tokens, doc_text, all_texts)
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k] if _ > 0]

    async def find_similar_documents(
        self,
        target_doc,
        all_documents: list,
        top_k: int = 5,
    ) -> list:
        """대상 문서와 유사한 문서 추천 (TF-IDF 코사인 유사도)"""
        candidates = [d for d in all_documents if d.id != target_doc.id]
        if not candidates:
            return []

        target_text = f"{target_doc.title} {target_doc.content_text or ''}"
        query_tokens = _tokenize(target_text)
        all_texts = [f"{d.title} {d.content_text or ''}" for d in candidates]

        scored = []
        for doc, doc_text in zip(candidates, all_texts):
            score = _tf_idf_score(query_tokens, doc_text, all_texts)
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    async def extract_key_topics(self, content: str) -> list[str]:
        """Gemini로 문서 핵심 토픽/태그 자동 추출"""
        _init_genai()
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        prompt = f"""다음 문서에서 핵심 토픽/키워드를 최대 10개 추출하세요.
JSON 배열로만 응답하세요: ["토픽1", "토픽2", ...]

문서:
{content[:8000]}"""
        try:
            response = model.generate_content(prompt)
            match = re.search(r"\[.*\]", response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        # 폴백: 빈도 기반 키워드
        tokens = _tokenize(content)
        freq: dict[str, int] = {}
        for t in tokens:
            if len(t) >= 2:
                freq[t] = freq.get(t, 0) + 1
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [t for t, _ in sorted_tokens[:10]]

    async def generate_document_summary(
        self, content: str, max_length: int = 200
    ) -> str:
        """Gemini로 문서 요약 자동 생성"""
        _init_genai()
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        prompt = f"""다음 문서를 {max_length}자 이내로 요약하세요. 핵심 내용만 간결하게 작성하세요.

문서:
{content[:10000]}

요약:"""
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"요약 생성 실패: {str(e)}"
