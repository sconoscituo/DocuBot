from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app.routers import users, documents, chats, payments
from app.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="DocuBot",
    description="AI 문서 Q&A 챗봇 빌더 (PDF/URL → 챗봇 자동 생성)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chats.router)
app.include_router(payments.router)


@app.get("/")
async def root():
    return {"service": config.APP_NAME, "status": "running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
