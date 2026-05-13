from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./nevo.db"
    secret_key: str = "nevo_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080
    model_path: str = "./ml/nevo_model.h5"
    class_indices_path: str = "./ml/class_indices.json"
    env: str = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()