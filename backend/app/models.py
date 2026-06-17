"""Database models for the application"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum

class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    DATASHEET = "datasheet"
    GA_DRAWING = "ga_drawing"

class MatchType(str, enum.Enum):
    """Match type enumeration"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    ML = "ml"
    BUSINESS_RULES = "business_rules"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user")

class Session(Base):
    """Review session model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    documents = relationship("Document", back_populates="session")
    comparisons = relationship("Comparison", back_populates="session")
    result = relationship("Result", back_populates="session", uselist=False)

class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    doc_type = Column(Enum(DocumentType))
    file_path = Column(String)
    original_filename = Column(String)
    extracted_text = Column(Text, nullable=True)
    extracted_tables = Column(Text, nullable=True)  # JSON string
    upload_time = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    
    session = relationship("Session", back_populates="documents")

class Comparison(Base):
    """Comparison result model"""
    __tablename__ = "comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    parameter = Column(String, index=True)  # tag_number, valve_size, etc.
    datasheet_value = Column(String, nullable=True)
    ga_value = Column(String, nullable=True)
    match_score = Column(Float)
    match_type = Column(Enum(MatchType))
    is_discrepancy = Column(Boolean, default=False)
    comment = Column(Text, nullable=True)
    confidence = Column(Float)  # Confidence score 0-1
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="comparisons")

class Result(Base):
    """Overall result model"""
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    overall_score = Column(Float)
    total_parameters = Column(Integer)
    matched_parameters = Column(Integer)
    discrepancy_count = Column(Integer)
    pdf_report_path = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="result")
