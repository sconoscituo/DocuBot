# DocuBot 설정 가이드

## 프로젝트 소개

PDF, Word 등 문서를 업로드하면 Gemini AI가 내용을 분석하여 자연어 질문에 답변해주는 문서 Q&A 챗봇 서비스입니다. 문서 요약, 핵심 내용 추출, 관련 섹션 검색 기능을 FastAPI 백엔드로 제공합니다.

---

## 1. 필요한 API 키 / 환경변수

| 변수명 | 설명 | 발급 URL |
|--------|------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API 키 | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `SECRET_KEY` | JWT 서명용 시크릿 키 | 직접 임의 문자열 생성 (32자 이상 권장) |
| `DATABASE_URL` | 데이터베이스 연결 URL | 기본값: `sqlite+aiosqlite:///./docubot.db` |
| `UPLOAD_DIR` | 업로드 파일 저장 경로 | 기본값: `./uploads` |
| `MAX_FILE_SIZE_MB` | 최대 업로드 파일 크기 (MB) | 기본값: `10` |
| `FREE_DOCUMENTS_LIMIT` | 무료 플랜 문서 업로드 제한 수 | 기본값: `3` |
| `FREE_QUESTIONS_LIMIT` | 무료 플랜 질문 제한 수 | 기본값: `50` |
| `DEBUG` | 디버그 모드 (true/false) | 기본값: `false` |

---

## 2. API 키 발급 방법

### GEMINI_API_KEY

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. **"Create API key"** 클릭
4. 발급된 키 복사

> Gemini 1.5 Flash 모델을 사용합니다. 무료 티어에서 분당 15회 요청 가능합니다.

### SECRET_KEY

JWT 토큰 서명용 키입니다. 터미널에서 아래 명령어로 생성:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 3. GitHub Secrets 설정

GitHub 레포지토리 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|------------|-----|
| `GEMINI_API_KEY` | Google AI Studio API 키 |
| `SECRET_KEY` | JWT 서명 시크릿 키 |

---

## 4. 로컬 개발 환경 설정

### 사전 요구사항

- Python 3.11 이상
- pip
- (선택) Docker, Docker Compose

### 설치 순서

```bash
# 1. 저장소 클론
git clone https://github.com/sconoscituo/DocuBot.git
cd DocuBot

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 파일 생성
cp .env.example .env

# 5. 업로드 디렉토리 생성
mkdir -p uploads
```

### .env 파일 편집

```env
APP_NAME=DocuBot
DEBUG=false
SECRET_KEY=여기에_32자_이상의_임의_문자열_입력
DATABASE_URL=sqlite+aiosqlite:///./docubot.db

GEMINI_API_KEY=AIzaSy...

UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
FREE_DOCUMENTS_LIMIT=3
FREE_QUESTIONS_LIMIT=50
```

---

## 5. 실행 방법

### 로컬 직접 실행

```bash
# 가상환경 활성화 후
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버 주소: `http://localhost:8000`
API 문서: `http://localhost:8000/docs`

### Docker로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 6. 주요 기능 사용법

### 회원가입 / 로그인

```bash
# 회원가입
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 로그인 (JWT 토큰 발급)
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 문서 업로드

지원 파일 형식: **PDF**, **HTML/웹페이지 텍스트**

```bash
# PDF 문서 업로드
curl -X POST http://localhost:8000/api/documents \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@/path/to/document.pdf" \
  -F "title=내 문서 제목"

# 업로드된 문서 목록 조회
curl http://localhost:8000/api/documents \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 문서 질문 (Q&A)

```bash
# 업로드한 문서에 질문
curl -X POST http://localhost:8000/api/chats \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "question": "이 문서의 핵심 내용을 요약해줘"
  }'

# 채팅 히스토리 조회
curl http://localhost:8000/api/chats?document_id=1 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 문서 요약 예시 질문

- `"이 문서를 3줄로 요약해줘"`
- `"3장의 주요 내용은 무엇인가요?"`
- `"계약 조건에 대해 설명해줘"`
- `"이 보고서의 결론은 무엇인가요?"`

### 문서 삭제

```bash
curl -X DELETE http://localhost:8000/api/documents/1 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 무료 플랜 제한

- 문서 업로드: 최대 3개
- 질문 횟수: 총 50회
- 최대 파일 크기: 10MB

### API 문서 (Swagger UI)

브라우저에서 `http://localhost:8000/docs` 접속 시 전체 API를 시각적으로 확인하고 테스트할 수 있습니다.
