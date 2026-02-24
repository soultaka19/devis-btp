from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/devis_btp"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "./uploads"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""

    # Email
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "devis@example.com"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
