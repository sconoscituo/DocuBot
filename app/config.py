from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    APP_NAME: str = "DocuBot"
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = "sqlite+aiosqlite:///./docubot.db"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    FREE_DOCUMENTS_LIMIT: int = 3
    FREE_QUESTIONS_LIMIT: int = 50

    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"


@lru_cache()
def get_config() -> Config:
    return Config()


config = get_config()
