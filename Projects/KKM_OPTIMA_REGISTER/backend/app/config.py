from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "KKM OPTIMA REGISTER"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://kkm:kkm@localhost:5432/kkm"
    jwt_secret: str = ""
    credential_encryption_key: str = ""
    access_token_minutes: int = 480
    upload_dir: str = "/data/uploads"
    max_file_size_mb: int = 15
    manager_1_username: str = "manager1"
    manager_1_password: str = ""
    manager_2_username: str = "manager2"
    manager_2_password: str = ""
    manager_3_username: str = "manager3"
    manager_3_password: str = ""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
