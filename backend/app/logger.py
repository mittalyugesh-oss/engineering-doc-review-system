"""Logging configuration"""
from loguru import logger
from app.config import get_settings
import os

settings = get_settings()

# Remove default handler
logger.remove()

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)

# Add file handler
logger.add(
    settings.log_file,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.log_level,
    rotation="500 MB",
    retention="7 days",
)

# Add console handler
logger.add(
    lambda msg: print(msg, end=""),
    format="{time:HH:mm:ss} | {level: <8} | {message}",
    level=settings.log_level,
)

def get_logger(name: str):
    """Get a logger instance"""
    return logger.bind(name=name)
