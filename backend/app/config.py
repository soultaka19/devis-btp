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

    # LLM provider — any endpoint exposing the OpenAI API works.
    # Default: Google Gemini through its OpenAI-compatible layer.
    LLM_API_KEY: str = ""
    LLM_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    # Text parsing (function calling) and audio transcription both run on this
    # model: Gemini has no /audio/transcriptions endpoint, so transcription goes
    # through chat/completions with an `input_audio` part (see voice_service).
    LLM_MODEL: str = "gemini-3.6-flash"

    # Deprecated: kept so an existing .env carrying only OPENAI_API_KEY keeps
    # working. `llm_api_key` below prefers LLM_API_KEY when both are present.
    OPENAI_API_KEY: str = ""

    # Storage (local filesystem, served under /uploads)
    STORAGE_LOCAL_PATH: str = "./uploads"

    # Email
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "devis@example.com"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:4200"]

    # --- Public demonstration ---------------------------------------------
    # Disposable sandbox: one user per visitor, erased at expiry.
    DEMO_LIFETIME_MINUTES: int = 60
    DEMO_MAX_LIVE_SANDBOXES: int = 50
    # Creations allowed per IP address per window.
    DEMO_RATE_LIMIT: int = 3
    DEMO_RATE_WINDOW_MINUTES: int = 10
    DEMO_CLEANUP_INTERVAL_SECONDS: int = 300

    # --- Model call budget --------------------------------------------------
    # REAL calls granted to a sandbox. An input already seen is served from the
    # cache and consumes nothing: the budget is therefore only spent when the
    # visitor submits something new.
    DEMO_AI_CALLS: int = 5
    # Global ceilings, in dollars. They protect the bill even if the per-IP
    # limit is bypassed, since they depend on no header.
    LLM_DAILY_BUDGET_USD: float = 0.50
    LLM_MONTHLY_BUDGET_USD: float = 5.00
    # gemini-3.6-flash pricing as of 2026-08-31, per million tokens. Reasoning
    # tokens are billed at the OUTPUT rate: that is why we count what the API
    # reports in `usage`, never an estimate.
    LLM_PRICE_INPUT_PER_M: float = 0.75
    LLM_PRICE_OUTPUT_PER_M: float = 3.75

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def llm_api_key(self) -> str:
        """Provider key, falling back to the legacy OpenAI variable."""
        return self.LLM_API_KEY or self.OPENAI_API_KEY

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
