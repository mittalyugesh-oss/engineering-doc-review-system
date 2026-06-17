"""Configuration settings for the application"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Configuration
    app_name: str = "Engineering Document Review System"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False") == "True"
    
    # Server Configuration
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", 8000))
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./engineering_doc_review.db")
    
    # File Upload Configuration
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", 50000000))  # 50MB
    allowed_extensions: list = ["pdf", "jpg", "jpeg", "png", "tiff"]
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    allowed_origins: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # ML/NLP Configuration
    spacy_model: str = "en_core_web_sm"
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    
    # OCR Configuration
    ocr_threshold: float = float(os.getenv("OCR_THRESHOLD", 0.5))
    tesseract_path: str = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
    
    # Matching Configuration
    fuzzy_match_threshold: float = 0.85
    semantic_match_threshold: float = 0.75
    overall_score_threshold: float = 0.75
    
    # Weights for hybrid matching
    exact_match_weight: float = 0.3
    fuzzy_match_weight: float = 0.2
    semantic_match_weight: float = 0.2
    ml_score_weight: float = 0.2
    business_rules_weight: float = 0.1
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/app.log")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    return Settings()
