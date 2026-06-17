# Engineering Document Review System Architecture

## Project Overview
AI/ML-powered system for verifying vendor-submitted GA (General Arrangement) drawings against instrument datasheets using hybrid comparison approach.

## System Architecture

The system uses a multi-layer architecture combining rule-based and machine learning approaches:

### Input Layer
- GA Drawing (Image/PDF)
- Instrument Datasheet (PDF)

### Document Processing Layer
- Image text extraction (Tesseract OCR) with preprocessing
- PDF text and table extraction (PyPDF2/pdfplumber)
- Unified data format (JSON/Dictionary)

### Information Extraction Layer (Hybrid)
**Method 1: Rule-Based Extraction (60% weight)**
- Direct pattern matching
- Fixed delimiters
- Table parsing
- Known format recognition
- Database lookups

**Method 2: ML-Based Extraction (40% weight)**
- Named Entity Recognition (spaCy)
- Context-aware extraction
- Fuzzy matching
- Semantic similarity (Sentence Transformers)

### Parameter Extraction & Validation
Extracts 11 key parameters with unit normalization and format standardization

### Comparison Engine (Hybrid)
**Exact Matching Algorithm**
- String equality
- Numeric range validation
- Unit conversion
- Database verification

**Semantic/Fuzzy Matching**
- Levenshtein distance
- Word embeddings
- Synonym matching
- Abbreviation expansion

### Discrepancy Detection
- Parameter mismatch identification
- Severity classification
- Missing parameter detection
- Root cause analysis

### Reporting Layer
- JSON reports (structured data)
- PDF reports (formatted documents)
- HTML reports (web viewing)
- Web Dashboard (Streamlit)

## Hybrid Confidence Scoring

```
For each parameter:
  Rule_Based_Confidence × 0.6 + ML_Based_Confidence × 0.4

Result Classification:
- High (>0.85): Accept match
- Medium (0.70-0.85): Manual review
- Low (<0.70): Flag as mismatch
```

## Data Flow

1. INPUT: Document files
2. PREPROCESSING: OCR, PDF extraction, image enhancement
3. TEXT NORMALIZATION: Lowercase, noise removal
4. RULE-BASED EXTRACTION: Regex, table parsing
5. ML-BASED EXTRACTION: NER, embeddings
6. CONFIDENCE SCORING: Weighted combination
7. PARAMETER MAPPING: GA ↔ Datasheet matching
8. COMPARISON & MATCHING: Fuzzy and semantic
9. DISCREPANCY DETECTION: Issue identification
10. REPORT GENERATION: Multi-format output

## Technology Stack

### Core Technologies
- **Python 3.8+**: Programming language
- **OpenCV**: Image processing
- **Tesseract**: OCR engine
- **PyPDF2/pdfplumber**: PDF processing

### NLP & ML
- **spaCy 3.6**: Named Entity Recognition
- **Sentence Transformers**: Semantic similarity
- **FuzzyWuzzy**: String matching
- **scikit-learn**: ML utilities

### Web & API
- **FastAPI**: REST API framework
- **Streamlit**: Web dashboard
- **Uvicorn**: ASGI server

### Database
- **SQLite**: Local database
- **SQLAlchemy**: ORM
- **Faiss**: Vector search

### Reporting
- **ReportLab**: PDF generation
- **Matplotlib**: Charts
- **Plotly**: Interactive visualizations

## Development Phases

### Phase 1: Core Processing
- Document ingestion
- Text extraction
- Basic parameter extraction

### Phase 2: Advanced Extraction
- NER model training
- Fuzzy matching
- Confidence scoring

### Phase 3: Comparison Engine
- Hybrid matching
- Discrepancy detection
- Report generation

### Phase 4: Web Interface
- REST API
- Dashboard
- Database integration