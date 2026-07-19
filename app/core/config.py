from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sim-Deutsch-BE"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:5173"
    ]

    # Logging Settings
    LOG_LEVEL: str = "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "dev"  # Options: "dev" or "prod" (JSON)

    DATABASE_URL: str = "sqlite:///./sim_deutsch.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Safely ignores any extra variables in .env that aren't defined here
    )


settings = Settings()
