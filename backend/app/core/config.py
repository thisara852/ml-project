import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Sri Lanka Tourism ML Recommendation & Trip Planning System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sri-lanka-paradise-island-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # SQLite default with seamless PostgreSQL switch via env
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sri_lanka_tourism.db')}"
    )


settings = Settings()
