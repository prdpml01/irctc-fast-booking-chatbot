"""Production-ready configuration and environment setup."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load config from .env or environment variables."""

    app_name: str = "IRCTC Fast Booking Chatbot"
    debug: bool = False
    log_level: str = "INFO"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
