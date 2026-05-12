import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Google Drive AI Assistant"
    API_V1_STR: str = "/api/v1"
    
    # LLM settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Drive settings - support multiple environment variable names
    # Priority order:
    # 1. GOOGLE_CREDENTIALS_JSON (raw JSON string)
    # 2. GOOGLE_APPLICATION_CREDENTIALS (file path)
    # 3. GOOGLE_DRIVE_CREDENTIALS_JSON (alternative name)
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    GOOGLE_CREDENTIALS_JSON: str = os.getenv("GOOGLE_CREDENTIALS_JSON", os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON", ""))
    
    # Folder ID - support multiple environment variable names
    DRIVE_FOLDER_ID: str = os.getenv("DRIVE_FOLDER_ID", os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""))
    
    # Frontend settings
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=".env",
        extra="ignore"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        logger.info("=" * 70)
        logger.info("CONFIGURATION LOADED")
        logger.info("=" * 70)
        logger.info(f"PROJECT_NAME: {self.PROJECT_NAME}")
        logger.info(f"GROQ_API_KEY: {'✅ Set' if self.GROQ_API_KEY else '❌ Not set'}")
        logger.info(f"OPENAI_API_KEY: {'✅ Set' if self.OPENAI_API_KEY else '❌ Not set'}")
        logger.info(f"GOOGLE_APPLICATION_CREDENTIALS: {self.GOOGLE_APPLICATION_CREDENTIALS}")
        logger.info(f"GOOGLE_CREDENTIALS_JSON: {'✅ Set' if self.GOOGLE_CREDENTIALS_JSON else '❌ Not set'}")
        logger.info(f"DRIVE_FOLDER_ID: {'✅ Set' if self.DRIVE_FOLDER_ID else '❌ Not set (will search all files)'}")
        logger.info(f"BACKEND_URL: {self.BACKEND_URL}")
        logger.info("=" * 70)

settings = Settings()

