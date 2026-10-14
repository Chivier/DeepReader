"""
Configuration module for DeepReader web interface
"""

import os
from runtime import BOOK_PROMPT_DIR, CHAT_HISTORY_DIR, BOOKMARKS_DIR
from typing import Optional

class Config:
    """Configuration class for DeepReader"""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL_NAME: str = os.getenv("DEEPREADER_MODEL_NAME", "gpt-4.1")
    
    # Application Settings
    APP_TITLE: str = "DeepReader - 深度读书"
    APP_ICON: str = "📚"
    
    # File Paths
    BOOK_PROMPT_DIR: str = str(BOOK_PROMPT_DIR)
    CHAT_HISTORY_DIR: str = str(CHAT_HISTORY_DIR)
    BOOKMARKS_DIR: str = str(BOOKMARKS_DIR)
    
    # Processing Settings
    DEFAULT_DOUBAN_COUNT: int = 1
    DEFAULT_MAX_VIDEOS: int = 3
    MIN_VIDEO_DURATION: int = 300  # 5 minutes in seconds
    
    # UI Settings
    DEFAULT_LAYOUT: str = "wide"
    SIDEBAR_WIDTH: int = 300
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set")
            return False
        return True
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration for API calls"""
        return {
            "model": cls.MODEL_NAME,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

# Development configuration
class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

# Production configuration  
class ProductionConfig(Config):
    """Production-specific configuration"""
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development")
if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()