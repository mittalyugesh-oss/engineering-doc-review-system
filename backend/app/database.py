"""Database configuration and initialization"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.config import get_settings
import os

settings = get_settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Database setup
if settings.database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL or other database
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
