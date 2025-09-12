from pydantic_settings import BaseSettings  # correct for Pydantic v2

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Async Template"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str

    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
