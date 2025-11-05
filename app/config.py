from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings.

    Loads configuration from environment variables or .env file.
    Provides settings for API prefix, database URL, and OIDC configuration.
    """

    model_config = SettingsConfigDict(env_file=".env")

    API_PREFIX: str = ""
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    OIDC_CONFIG_URL: str | None = None
    LOG_LEVEL: str = "INFO"


settings = Settings()
