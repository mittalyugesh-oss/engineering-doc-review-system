# Engineering Document Review System - Architecture

## System Overview
AI/ML-based document review system for verifying GA drawings against instrument datasheets using hybrid comparison approach.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB INTERFACE (React)                   │
│              File Upload & Results Dashboard                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ API Endpoints:                                          ││
│  │ - /upload (multipart form)                              ││
│  │ - /process (analyze documents)                          ││
│  │ - /results (get comparison results)                     ││
│  │ - /export-pdf (generate comment sheet)                  ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────┬──────────────────────────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼──────────────┐  ┌──▼─────────────────┐
│ PROCESSING LAYER │  │ ML/NLP LAYER       │
│                  │  │                    │
│ • PDF Parser     │  │ • Text Extraction  │
│ • Image-to-Text  │  │ • Entity Extraction│
│ • Table Extractor│  │ • Similarity Match │
│ • Data Normalizer│  │ • Validation Logic │
└───┬──────────────┘  └──┬─────────────────┘
    │                    │
    └────────┬───────────┘
             │
    ┌────────▼──────────────────┐
    │  COMPARISON ENGINE        │
    │                           │
    │ Hybrid Matching:          │
    │ 1. Exact Match            │
    │ 2. Fuzzy Match (Levensh.)│
    │ 3. Semantic Match (NLP)   │
    │ 4. ML Classifier          │
    │ 5. Domain Rules           │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────────────┐
    │  RESULT GENERATION        │
    │                           │
    │ • Comparison Report       │
    │ • Discrepancies Flag      │
    │ • Confidence Scores       │
    │ • PDF Comment Sheet       │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────────────┐
    │  DATABASE (SQLite)        │
    │                           │
    │ • Sessions                │
    │ • Document Records        │
    │ • Comparison Results      │
    │ • User Feedback           │
    └───────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (async, modern Python web framework)
- **Server**: Uvicorn (ASGI server)
- **Database**: SQLite with SQLAlchemy ORM

### Document Processing
- **PDF Processing**: PyPDF2, pdfplumber (text extraction, table parsing)
- **Image Processing**: Pillow, OpenCV
- **OCR**: Tesseract (via pytesseract) + EasyOCR for fallback
- **Table Detection**: Camelot (table extraction from PDFs)

### ML/NLP
- **Text Processing**: NLTK, spaCy (entity recognition, tokenization)
- **Similarity**: Scikit-learn (fuzzy matching), sentence-transformers (semantic similarity)
- **ML Classification**: scikit-learn (SVM, RandomForest for validation)

### Frontend
- **Framework**: React.js
- **UI Components**: Material-UI
- **State Management**: Redux
- **HTTP Client**: Axios

### PDF Generation
- **Report Generation**: ReportLab + PyPDF2 (annotations)
- **Alternative**: WeasyPrint for HTML-to-PDF with comments

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose

## Core Components

### 1. Document Ingestion Module
```
Input: GA Drawing (PDF/Image) + Datasheet (PDF)
       ↓
   ├─ PDF Extract (text, tables, images)
   ├─ Image OCR (Tesseract + EasyOCR)
   ├─ Table Parser (Camelot for structured data)
   └─ Validator (schema validation)
```

### 2. Data Extraction Module
Target Parameters:
- Tag Number
- Valve Size
- Valve Type
- Class/Rating
- Body Material
- Trim Material
- Failure Position

### 3. Hybrid Comparison Engine
```
Stage 1: EXACT MATCH
  - Direct string comparison
  - Case-insensitive, whitespace normalized

Stage 2: FUZZY MATCH
  - Levenshtein distance
  - Threshold: 85% similarity

Stage 3: SEMANTIC MATCH
  - Word embeddings (sentence-transformers)
  - Domain-specific dictionaries
  - Material/Valve type mappings

Stage 4: ML CLASSIFIER
  - Trained on domain data
  - Confidence scoring
  - Anomaly detection

Stage 5: BUSINESS RULES
  - Unit conversion validation
  - Material compatibility checks
  - Standards compliance (ASME, API, ISO)
```

### 4. Scoring System
```
Final Score = w1×ExactMatch + w2×FuzzyMatch + w3×SemanticMatch + 
              w4×MLScore + w5×BusinessRules

Weights: [0.3, 0.2, 0.2, 0.2, 0.1]
Threshold for PASS: 0.75 (75%)
```

## Parameter Extraction Strategy

### Tag Number
- Regex patterns: `TAG-\d+`, `TAG\d+`, `T\d+`
- Location: Usually near top of drawing
- Backup: ML entity recognition

### Valve Size
- Units: inches (nominal), mm
- Patterns: `\d+/\d+"`, `\d+\.?\d*"`, `DN\d+`, `NPS\d+`
- Conversion lookup table

### Valve Type
- Domain dictionary: Gate, Globe, Check, Ball, Butterfly, Relief, etc.
- Fuzzy matching against known types

### Class/Rating
- Patterns: `150`, `300`, `600`, `900`, `1500`, `2500`
- Regex: `(Class|ANSI|DIN)\s*\d+`

### Body Material
- Domain knowledge: CI, CS, SS, ASTM grades
- Material database lookup

### Trim Material
- Similar to body material with additional codes

### Failure Position
- Domain dictionary: Fail Safe Close (FSC), Fail Safe Open (FSO)
- Keywords: "fail", "position", "default"

## Data Flow

```
User Upload
    ↓
File Validation (type, size)
    ↓
[Async Processing]
    ├─ Extract GA Drawing Data
    ├─ Extract Datasheet Data
    │
    ├─ For Each of 7 Parameters:
    │  ├─ Extract from GA
    │  ├─ Extract from Datasheet
    │  ├─ Compare (hybrid approach)
    │  ├─ Generate Flag/Comment
    │  └─ Score result
    │
    ├─ Generate Comparison Report
    ├─ Identify Discrepancies
    └─ Calculate Overall Compliance
         ↓
Generate Comment Sheet PDF
    ↓
User Download
```

## Database Schema

```
Users
├─ id (PK)
├─ email
├─ created_at

Sessions
├─ id (PK)
├─ user_id (FK)
├─ created_at
├─ status (pending, processing, completed)

Documents
├─ id (PK)
├─ session_id (FK)
├─ doc_type (datasheet/ga_drawing)
├─ file_path
├─ extracted_text
├─ upload_time

Comparisons
├─ id (PK)
├─ session_id (FK)
├─ parameter (tag_number, valve_size, etc.)
├─ datasheet_value
├─ ga_value
├─ match_score
├─ match_type (exact/fuzzy/semantic/ml)
├─ flag (discrepancy)
├─ comment

Results
├─ id (PK)
├─ session_id (FK)
├─ overall_score
├─ pdf_report_path
├─ created_at
```

## Security Considerations
- File upload validation (size, type)
- Virus scanning (ClamAV optional)
- Input sanitization
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration
- Rate limiting
- Session management

## Error Handling
- Graceful fallbacks (PDF → Image OCR)
- Detailed error logging
- User-friendly error messages
- Retry mechanisms for external services

## Deployment Options
1. **Local**: Docker Compose
2. **Cloud**: AWS (EC2, S3), Google Cloud, Azure
3. **Development**: Docker + hot reload

## Performance Metrics
- Document processing: < 30 seconds
- Comparison engine: < 5 seconds
- PDF generation: < 10 seconds
- Total end-to-end: < 50 seconds

## Future Enhancements
1. Machine learning model training on domain data
2. Real-time collaboration features
3. Audit trail and version control
4. Integration with PLM systems
5. Mobile app (React Native)
6. Advanced analytics dashboard
7. Custom rule builder UI
8. Multi-language support
