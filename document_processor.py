"""
Document Processing Module
Handles OCR extraction from images and text extraction from PDFs
"""
import cv2
import pytesseract
from PIL import Image
import PyPDF2
import pdfplumber
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from logger_config import logger


class ImageProcessor:
    """Process and extract text from images"""
    
    @staticmethod
    def preprocess_image(image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR performance
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image array
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Threshold
            _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)
            
            # Dilation and erosion
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            logger.info(f"Image preprocessing completed: {image_path}")
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            # Preprocess image
            processed_img = ImageProcessor.preprocess_image(image_path)
            
            # Convert back to PIL Image for pytesseract
            pil_image = Image.fromarray(processed_img)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image, lang='eng')
            
            logger.info(f"Text extracted from image: {image_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_tables_from_image(image_path: str) -> List[Dict]:
        """
        Extract table structures from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of detected table regions
        """
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect lines
            edges = cv2.Canny(gray, 100, 200)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            tables = []
            if lines is not None:
                # Group lines into table regions
                horizontal_lines = [l for l in lines if abs(l[0][1] - l[0][3]) < 5]
                vertical_lines = [l for l in lines if abs(l[0][0] - l[0][2]) < 5]
                
                tables.append({
                    "type": "grid_table",
                    "horizontal_lines": len(horizontal_lines),
                    "vertical_lines": len(vertical_lines),
                })
            
            logger.info(f"Table detection completed: {image_path}")
            return tables
            
        except Exception as e:
            logger.error(f"Error detecting tables in image {image_path}: {str(e)}")
            raise


class PDFProcessor:
    """Process and extract text from PDFs"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            logger.info(f"Text extracted from PDF: {pdf_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
        """
        Extract tables from PDF using pdfplumber
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of tables (each table is a list of rows)
        """
        try:
            tables = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            tables.append({
                                "page": page_num + 1,
                                "data": table,
                                "rows": len(table),
                                "cols": len(table[0]) if table else 0,
                            })
            
            logger.info(f"Tables extracted from PDF: {pdf_path} - Found {len(tables)} tables")
            return tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path}: {str(e)}")
            raise
    
    @staticmethod
    def extract_text_with_tables(pdf_path: str) -> Dict:
        """
        Extract both text and tables from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with text and tables
        """
        try:
            return {
                "text": PDFProcessor.extract_text_from_pdf(pdf_path),
                "tables": PDFProcessor.extract_tables_from_pdf(pdf_path),
            }
        except Exception as e:
            logger.error(f"Error extracting content from PDF {pdf_path}: {str(e)}")
            raise


class DocumentProcessor:
    """Main document processing interface"""
    
    @staticmethod
    def process_document(file_path: str) -> Dict:
        """
        Process document (image or PDF) and extract content
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()
        
        result = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "status": "success",
        }
        
        try:
            if file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                result["document_type"] = "image"
                result["text"] = ImageProcessor.extract_text_from_image(str(file_path))
                result["tables"] = ImageProcessor.extract_tables_from_image(str(file_path))
                
            elif file_ext == '.pdf':
                result["document_type"] = "pdf"
                content = PDFProcessor.extract_text_with_tables(str(file_path))
                result["text"] = content["text"]
                result["tables"] = content["tables"]
                
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            logger.info(f"Document processed successfully: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            result["status"] = "error"
            result["error"] = str(e)
            return result
    
    @staticmethod
    def process_batch(file_paths: List[str]) -> List[Dict]:
        """
        Process multiple documents
        
        Args:
            file_paths: List of document file paths
            
        Returns:
            List of processing results
        """
        results = []
        for file_path in file_paths:
            result = DocumentProcessor.process_document(file_path)
            results.append(result)
        
        return results


if __name__ == "__main__":
    # Example usage
    doc_processor = DocumentProcessor()
    
    # Process single document
    result = doc_processor.process_document("sample_ga_drawing.png")
    print(result)