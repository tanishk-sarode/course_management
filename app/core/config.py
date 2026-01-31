from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Course Enrollment API"
    app_version: str = "1.0.0"
    cors_origins: list[str] = ["*"]
    database_url: str = "sqlite:///./app.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Change this in production!

    class Config:
        env_file = ".env"

settings = Settings()