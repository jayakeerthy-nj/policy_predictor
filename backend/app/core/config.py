from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Polaris Policy Impact Intelligence API"
    app_version: str = "0.1.0"
    environment: str = "dev"

    postgres_url: str = Field(
        default="postgresql+psycopg2://polaris:polaris@postgres:5432/polaris"
    )
    redis_url: str = "redis://redis:6379/0"

    newsapi_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    hf_model_name: str = "ProsusAI/finbert"
    policy_confidence_threshold: float = 0.6


settings = Settings()

