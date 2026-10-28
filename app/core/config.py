import os
from typing import List

class Settings:
    """
    Application Settings
    Configured via environment variables (.env file).
    Protects sensitive credentials including database URL and AI API keys.
    """
    PROJECT_NAME: str = "BookLeaf Author Support & Communication Portal"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:root@localhost:5432/bookleaf_db"
    )

    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-bookleaf-jwt-key-2026")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # AI Configuration (OpenAI, Gemini, Claude, etc.)
    # Must NEVER be exposed to frontend
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-1.5-flash")

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ]

settings = Settings()
