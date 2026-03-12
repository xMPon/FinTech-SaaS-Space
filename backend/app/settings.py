from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = BASE_DIR / "app.db"


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    admin_token: str
    app_name: str = "FinTech SaaS Space MVP"
    model_config = SettingsConfigDict(env_prefix="FTSAAS_", env_file=".env")


settings = Settings()
