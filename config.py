"""
Configuration management for Engineering Document Review System
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSING_DIR = DATA_DIR / "processing"
RESULTS_DIR = DATA_DIR / "results"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOADS_DIR, PROCESSING_DIR, RESULTS_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OCR Configuration
OCR_CONFIG = {
    "language": "eng",
    "dpi": 300,
    "psm": 3,  # PSM 3: Fully automatic page segmentation with OSD
}

# ML Model Configuration
ML_CONFIG = {
    "sentence_transformer_model": "all-MiniLM-L6-v2",  # Lightweight, fast
    "spacy_model": "en_core_web_sm",
    "fuzzy_threshold": 0.80,
    "confidence_threshold": 0.70,
}

# Hybrid Approach Weights
HYBRID_WEIGHTS = {
    "rule_based": 0.6,
    "ml_based": 0.4,
}

# Confidence Score Thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.85,
    "medium": 0.70,
    "low": 0.0,
}

# Parameter Configuration
PARAMETERS_TO_EXTRACT = [
    "tag_number",
    "valve_size",
    "valve_type",
    "class_rating",
    "body_material",
    "trim_material",
    "failure_position",
    "seat_material",
    "bonnet_type",
    "port_size",
    "connection_type",
]

# Unit Conversion Mapping
UNIT_CONVERSIONS = {
    "mm_to_inch": 0.0393701,
    "inch_to_mm": 25.4,
    "kpa_to_bar": 0.01,
    "bar_to_kpa": 100,
}

# Material Database (for validation)
MATERIAL_DATABASE = {
    "body_materials": [
        "Carbon Steel", "Stainless Steel", "Cast Iron", "Ductile Iron",
        "Bronze", "Brass", "Aluminum", "Nickel Alloy", "ASTM A105", "ASTM A216"
    ],
    "trim_materials": [
        "Stainless Steel", "Carbon Steel", "Bronze", "PTFE", "Inconel",
        "Stellite", "Hastelloy", "Monel", "Ductile Iron"
    ],
    "seat_materials": [
        "PTFE", "Graphite", "Metal", "Soft Seated", "Hard Seated",
        "Full Port", "Reduced Port"
    ],
}

# Valve Type Database
VALVE_TYPES = [
    "Globe", "Gate", "Check", "Ball", "Butterfly", "Plug",
    "Diaphragm", "Needle", "Relief", "Safety", "Solenoid"
]

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/edrs.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "edrs.log"

# Processing Configuration
MAX_FILE_SIZE_MB = 50
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "tiff", "bmp"]
SUPPORTED_PDF_FORMATS = ["pdf"]
BATCH_PROCESSING_SIZE = 10

# Report Configuration
REPORT_FORMAT = "pdf"  # Can be "pdf", "json", "html"
REPORT_INCLUDE_IMAGES = True
REPORT_CONFIDENCE_THRESHOLD = 0.70