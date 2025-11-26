from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_SECRET: str = "secret"
    WEBHOOK_VERIFY_TOKEN: str = "token"

    class Config:
        env_file = ".env"

settings = Settings()
