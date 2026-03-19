# DocuBot

AI 문서 Q&A 챗봇 빌더 (PDF/URL → 챗봇 자동 생성)

## 기능

- PDF 업로드 또는 URL 크롤링으로 문서 등록
- Gemini AI 긴 컨텍스트를 활용한 문서 기반 Q&A
- 챗봇 공유 링크 생성
- 문서 요약 및 추천 질문 자동 생성
- JWT 인증 + 프리미엄 플랜 (무료: 문서 3개, 월 50회 질문)

## 시작하기

```bash
cp .env.example .env
# .env 파일에 API 키 설정

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up -d
```

## API 문서

서버 실행 후 http://localhost:8000/docs

## 환경 변수

| 변수 | 설명 |
|------|------|
| GEMINI_API_KEY | Google Gemini API 키 |
| SECRET_KEY | JWT 서명 키 |
| FREE_DOCUMENTS_LIMIT | 무료 플랜 문서 제한 (기본 3) |
| FREE_QUESTIONS_LIMIT | 무료 플랜 월 질문 제한 (기본 50) |
