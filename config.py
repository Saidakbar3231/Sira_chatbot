from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./sira.db"

    # Groq — 3 keys for rotation
    GROQ_API_KEY_1: str
    GROQ_API_KEY_2: str
    GROQ_API_KEY_3: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Vector store
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Admin
    ADMIN_IDS: list[int] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
