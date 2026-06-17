"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MatchType(str, Enum):
    """Match type enumeration"""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    ML = "ml"
    BUSINESS_RULES = "business_rules"

class ComparisonSchema(BaseModel):
    """Comparison result schema"""
    parameter: str
    datasheet_value: Optional[str] = None
    ga_value: Optional[str] = None
    match_score: float
    match_type: MatchType
    is_discrepancy: bool
    comment: Optional[str] = None
    confidence: float
    
    class Config:
        from_attributes = True

class ResultSchema(BaseModel):
    """Result schema"""
    overall_score: float
    total_parameters: int
    matched_parameters: int
    discrepancy_count: int
    summary: Optional[str] = None
    comparisons: List[ComparisonSchema] = []
    
    class Config:
        from_attributes = True

class SessionSchema(BaseModel):
    """Session schema"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    result: Optional[ResultSchema] = None
    
    class Config:
        from_attributes = True

class UploadResponseSchema(BaseModel):
    """Upload response schema"""
    session_id: int
    message: str
    status: str

class ProcessResponseSchema(BaseModel):
    """Process response schema"""
    session_id: int
    status: str
    progress: Optional[float] = None
    message: str

class ExportPDFResponseSchema(BaseModel):
    """Export PDF response schema"""
    session_id: int
    pdf_url: str
    message: str

class ErrorResponseSchema(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int
