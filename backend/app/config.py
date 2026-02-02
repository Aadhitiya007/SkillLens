"""
Configuration management for SkillLens backend.
Loads environment variables and provides application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "SkillLens"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # API URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # PostgreSQL
    database_url: str = "postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production-make-it-very-long-and-random"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours
    
    # OpenAI
    openai_api_key: Optional[str] = None
    gpt_model: str = "gpt-3.5-turbo"
    gpt_temperature: float = 0.7
    
    # Hugging Face
    huggingface_api_key: Optional[str] = None
    sentence_bert_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # SerpAPI
    serpapi_key: Optional[str] = None
    
    # Feature Flags
    enable_github_analysis: bool = False
    enable_job_intelligence: bool = True
    enable_predictions: bool = True
    
    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [".pdf", ".docx", ".doc"]
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def validate_api_keys(self) -> dict[str, bool]:
        """Validate that required API keys are present."""
        return {
            "openai": self.openai_api_key is not None,
            "huggingface": self.huggingface_api_key is not None,
            "serpapi": self.serpapi_key is not None if self.enable_job_intelligence else True,
        }


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
