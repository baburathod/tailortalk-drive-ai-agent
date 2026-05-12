import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Google Drive AI Assistant"
    API_V1_STR: str = "/api/v1"
    
    # LLM settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Drive settings
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    DRIVE_FOLDER_ID: str = os.getenv("DRIVE_FOLDER_ID", "")
    
    # Frontend settings that might be in the .env file
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    model_config = SettingsConfigDict(
        case_sensitive=True, 
        env_file=".env",
        extra="ignore" # This prevents the 'extra_forbidden' error
    )

settings = Settings()
