"""
Logging configuration
"""
import sys
from loguru import logger
from config import LOG_FILE, LOG_LEVEL

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=LOG_LEVEL,
)

# Add file handler
logger.add(
    str(LOG_FILE),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=LOG_LEVEL,
    rotation="10 MB",
    retention="10 days",
)

__all__ = ["logger"]