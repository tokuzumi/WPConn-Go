from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_SECRET: str
    WEBHOOK_VERIFY_TOKEN: str
    
    # MinIO Settings
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_USE_SSL: bool = True

    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
