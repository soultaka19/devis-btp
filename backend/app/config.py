import logging

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

# Example values shipped in .env.example / docker-compose files: never valid in production
PLACEHOLDER_SECRET_KEYS = {
    "change-me-in-production",
    "change-me-in-production-use-openssl-rand-hex-32",
    "dev-secret-key-change-in-production",
}
MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    # "development" (default) or "production"
    APP_ENV: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/devis_btp"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Storage (local filesystem, served under /uploads)
    STORAGE_LOCAL_PATH: str = "./uploads"

    # Email
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "devis@example.com"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("SECRET_KEY")
    @classmethod
    def check_secret_key(cls, key: str, info: ValidationInfo) -> str:
        """Refuse a weak/placeholder SECRET_KEY in production (JWT would be forgeable).

        APP_ENV is declared before SECRET_KEY, so it is already available in info.data.
        """
        if not key:
            problem = "SECRET_KEY est vide"
        elif key in PLACEHOLDER_SECRET_KEYS:
            problem = "SECRET_KEY est une valeur d'exemple"
        elif len(key) < MIN_SECRET_KEY_LENGTH:
            problem = f"SECRET_KEY fait moins de {MIN_SECRET_KEY_LENGTH} caractères"
        else:
            return key

        app_env = info.data.get("APP_ENV", "development")
        message = f"{problem} : générez une clé avec `openssl rand -hex 32`"
        if app_env == "production":
            raise ValueError(message)
        logger.warning("%s (toléré car APP_ENV=%s)", message, app_env)
        return key


settings = Settings()
