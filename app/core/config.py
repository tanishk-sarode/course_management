from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Settings(BaseSettings):
    """
    Application configuration loaded from .env file.
    All global variables should be defined here.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )
    
    # -------- APPLICATION SETTINGS --------
    app_name: str = os.getenv("APP_NAME", "FastAPI Application")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # -------- CORS SETTINGS --------
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    
    # -------- DATABASE SETTINGS --------
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # -------- JWT/SECURITY SETTINGS --------
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # -------- BCRYPT SETTINGS --------
    BCRYPT_LOG_ROUNDS: int = 12  # Number of rounds for bcrypt hashing (higher = more secure but slower)

    def get_cors_origins_list(self) -> list[str]:
        """Convert comma-separated string to list of origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# -------- GLOBAL SETTINGS INSTANCE --------
settings = Settings()