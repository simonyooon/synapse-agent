"""
Configuration management for Synapse using Pydantic BaseSettings.
Loads settings from environment variables and .env file.
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Main settings class for Synapse."""
    
    # API Keys
    slack_bot_token: str
    openai_api_key: str
    github_token: str
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # MLflow Configuration
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "synapse"
    
    # OpenAI Configuration
    openai_model: str = "gpt-4-turbo-preview"
    openai_max_tokens: int = 500
    openai_temperature: float = 0.3
    
    # GitHub Configuration
    github_default_repo: Optional[str] = None
    github_default_labels: List[str] = ["bug", "enhancement", "documentation", "question"]
    
    # Cache Configuration
    cache_ttl: int = 3600  # 1 hour default TTL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings instance
    """
    return Settings() 