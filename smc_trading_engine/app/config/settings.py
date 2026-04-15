from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "INFO"
    bitunix_base_url: str = ""
    bitunix_api_key: str = ""
    bitunix_api_secret: str = ""
    bitunix_passphrase: str = ""
    default_leverage: int = 20
    pair_cooldown_minutes: int = 30
    min_confidence_score: float = 0.70
    db_url: str = "sqlite:///./smc_engine.db"
    redis_url: str = ""
    telegram_admin_ids: str = ""
    telegram_auth_enabled: bool = False
    scan_interval_seconds: int = 20
    default_timeframes: str = "1m,5m,15m,1h"


settings = Settings()
