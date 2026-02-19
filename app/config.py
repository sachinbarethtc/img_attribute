import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    MAX_RETRIES: int = 3
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
