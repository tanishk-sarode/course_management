from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

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
    app_name: str = "Online Learning Platform"
    app_version: str = "1.0.0"
    
    # -------- CORS SETTINGS --------
    cors_origins: str = "*"
    
    # -------- DATABASE SETTINGS --------
    database_url: str = "sqlite:///./app.db"
    
    # -------- JWT/SECURITY SETTINGS --------
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # -------- BCRYPT SETTINGS --------
    BCRYPT_LOG_ROUNDS: int = 12  # Number of rounds for bcrypt hashing (higher = more secure but slower)

    def get_cors_origins_list(self) -> list[str]:
        """Convert comma-separated string to list of origins."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


# -------- GLOBAL SETTINGS INSTANCE --------
settings = Settings()