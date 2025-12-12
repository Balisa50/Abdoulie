import os
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Tesseract SaaS MVP"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_RANDOM_SECRET"
    require_api_key: bool = False
    api_keys: list[str] = []
    enable_rate_limiting: bool = True
    rate_limit_calls: int = 100
    rate_limit_period: int = 60

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    # Database
    database_url: str = "postgresql+asyncpg://tesseract:tesseract@postgres:5432/tesseract"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    redis_url: str = "redis://redis:6379/0"

    # AWS
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = "http://localstack:4566"
    s3_bucket_name: str = "tesseract-uploads"
    sqs_queue_name: str = "tesseract-tasks"

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = [".pdf"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v: Any) -> list[str]:
        """Parse comma-separated API keys from environment."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v or []

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {', '.join(allowed)}")
        return v.lower()

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


def validate_production_settings(settings: Settings) -> list[str]:
    """Validate critical settings for production deployment."""
    issues = []

    if settings.is_production:
        # Check secret key
        if settings.secret_key == "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_RANDOM_SECRET":
            issues.append("SECRET_KEY must be changed in production")

        # Check debug mode
        if settings.debug:
            issues.append("DEBUG must be False in production")

        # Check API key requirement
        if not settings.require_api_key:
            issues.append("REQUIRE_API_KEY should be True in production")

        # Check database credentials
        if "tesseract:tesseract" in settings.database_url:
            issues.append("Default database credentials detected - use strong credentials")

        # Check AWS credentials
        if settings.aws_access_key_id == "test" or settings.aws_secret_access_key == "test":
            issues.append("AWS credentials must be configured for production")

        # Check CORS origins
        if "localhost" in " ".join(settings.cors_origins):
            issues.append("CORS origins should not include localhost in production")

    return issues


settings = Settings()

# Validate production settings on startup
if settings.is_production:
    production_issues = validate_production_settings(settings)
    if production_issues:
        error_msg = "Production configuration issues:\n" + "\n".join(f"  - {issue}" for issue in production_issues)
        raise RuntimeError(error_msg)
