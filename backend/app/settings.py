from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Tesseract SaaS MVP"
    app_version: str = "0.1.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://tesseract:tesseract@postgres:5432/tesseract"
    redis_url: str = "redis://redis:6379/0"

    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "us-east-1"
    aws_endpoint_url: str | None = "http://localstack:4566"
    s3_bucket_name: str = "tesseract-uploads"
    sqs_queue_name: str = "tesseract-tasks"

    cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]


settings = Settings()
