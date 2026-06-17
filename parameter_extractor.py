"""
Rule-Based Parameter Extraction Module (60% of Hybrid Approach)
"""
import re
from typing import Dict, List, Tuple, Optional
import pandas as pd
from logger_config import logger
from config import PARAMETERS_TO_EXTRACT, UNIT_CONVERSIONS, MATERIAL_DATABASE, VALVE_TYPES


class RuleBasedExtractor:
    """Rule-based parameter extraction using patterns and regex"""
    
    # Regex patterns for parameter extraction
    PATTERNS = {
        "tag_number": r"(?:TAG|Tag|tag|ID|id)\s*[:#]?\s*([A-Z0-9\-_]+)",
        "valve_size": r"(?:Size|size|SIZE)\s*[:#]?\s*(\d+(?:\.\d+)?)\s*(?:mm|MM|in|IN)?",
        "valve_type": r"(?:Type|type|TYPE)\s*[:#]?\s*(" + "|".join(VALVE_TYPES) + r")",
        "class_rating": r"(?:Class|class|CLASS|Rating|rating|RATING)\s*[:#]?\s*([A-Z0-9\s\.]+?)(?:\n|$)",
        "body_material": r"(?:Body\s+Material|body\s+material|Body Mat\.?)\s*[:#]?\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
        "trim_material": r"(?:Trim|trim|Internal Material)\s*[:#]?\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
        "failure_position": r"(?:Failure\s+(?:Position|Mode)|Fail\s*(?:Safe|Action))\s*[:#]?\s*([A-Za-z\s\-]+?)(?:\n|$)",
        "seat_material": r"(?:Seat|seat|Seating)\s*[:#]?\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
        "bonnet_type": r"(?:Bonnet|bonnet|Bonnet Type)\s*[:#]?\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
        "port_size": r"(?:Port|port|Outlet)\s*(?:Size|size|DIA)\s*[:#]?\s*(\d+(?:\.\d+)?)\s*(?:mm|MM|in|IN)?",
        "connection_type": r"(?:Connection|connection|Connect)\s*[:#]?\s*([A-Za-z0-9\s\-]+?)(?:\n|$)",
    }
    
    @staticmethod
    def extract_tag_number(text: str) -> Tuple[Optional[str], float]:
        """Extract Tag Number using regex"""
        pattern = RuleBasedExtractor.PATTERNS["tag_number"]
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            tag = match.group(1).strip()
            if tag and len(tag) > 0:
                logger.debug(f"Tag number extracted: {tag}")
                return tag, 0.95  # High confidence for direct matches
        
        return None, 0.0
    
    @staticmethod
    def extract_valve_size(text: str) -> Tuple[Optional[str], float]:
        """Extract Valve Size"""
        pattern = RuleBasedExtractor.PATTERNS["valve_size"]
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            size = match.group(1).strip()
            if size and size.isdigit():
                logger.debug(f"Valve size extracted: {size}")
                return size, 0.90
        
        return None, 0.0
    
    @staticmethod
    def extract_valve_type(text: str) -> Tuple[Optional[str], float]:
        """Extract Valve Type"""
        for valve_type in VALVE_TYPES:
            if re.search(rf"\b{valve_type}\b", text, re.IGNORECASE):
                logger.debug(f"Valve type extracted: {valve_type}")
                return valve_type, 0.92
        
        return None, 0.0
    
    @staticmethod
    def extract_class_rating(text: str) -> Tuple[Optional[str], float]:
        """Extract Class/Rating"""
        pattern = RuleBasedExtractor.PATTERNS["class_rating"]
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            rating = match.group(1).strip()
            logger.debug(f"Class/Rating extracted: {rating}")
            return rating, 0.85
        
        return None, 0.0
    
    @staticmethod
    def extract_from_table(table_data: List[List[str]], parameter: str) -> Tuple[Optional[str], float]:
        """
        Extract parameter from table data
        
        Args:
            table_data: 2D list representing table rows and columns
            parameter: Parameter name to extract
            
        Returns:
            Tuple of (value, confidence_score)
        """
        try:
            df = pd.DataFrame(table_data[1:], columns=table_data[0])
            
            # Search for column header matching the parameter
            matching_columns = [col for col in df.columns if parameter.lower().replace('_', ' ') in col.lower()]
            
            if matching_columns:
                value = df[matching_columns[0]].iloc[0]
                logger.debug(f"Parameter '{parameter}' extracted from table: {value}")
                return str(value), 0.88
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Error extracting '{parameter}' from table: {str(e)}")
            return None, 0.0
    
    @staticmethod
    def extract_material(text: str, material_type: str) -> Tuple[Optional[str], float]:
        """
        Extract material with database validation
        
        Args:
            text: Text to search in
            material_type: 'body_materials', 'trim_materials', or 'seat_materials'
            
        Returns:
            Tuple of (material, confidence_score)
        """
        materials = MATERIAL_DATABASE.get(material_type, [])
        
        for material in materials:
            if re.search(rf"\b{material}\b", text, re.IGNORECASE):
                logger.debug(f"Material extracted: {material}")
                return material, 0.90
        
        return None, 0.0
    
    @staticmethod
    def normalize_numeric(value: str, unit_from: str, unit_to: str) -> Optional[float]:
        """
        Normalize numeric values across units
        
        Args:
            value: Numeric value as string
            unit_from: Source unit
            unit_to: Target unit
            
        Returns:
            Normalized value
        """
        try:
            num_value = float(re.sub(r'[^\d\.]', '', value))
            conversion_key = f"{unit_from}_to_{unit_to}"
            
            if conversion_key in UNIT_CONVERSIONS:
                return num_value * UNIT_CONVERSIONS[conversion_key]
            
            return num_value
            
        except Exception as e:
            logger.error(f"Error normalizing value {value}: {str(e)}")
            return None
    
    @staticmethod
    def extract_all_parameters(text: str, tables: List[Dict]) -> Dict:
        """
        Extract all 11 parameters from text and tables
        
        Args:
            text: Extracted text from document
            tables: Extracted tables from document
            
        Returns:
            Dictionary of extracted parameters with confidence scores
        """
        results = {
            "extraction_method": "rule_based",
            "parameters": {},
        }
        
        # Extract from text
        results["parameters"]["tag_number"] = {
            "value": RuleBasedExtractor.extract_tag_number(text)[0],
            "confidence": RuleBasedExtractor.extract_tag_number(text)[1],
        }
        
        results["parameters"]["valve_size"] = {
            "value": RuleBasedExtractor.extract_valve_size(text)[0],
            "confidence": RuleBasedExtractor.extract_valve_size(text)[1],
        }
        
        results["parameters"]["valve_type"] = {
            "value": RuleBasedExtractor.extract_valve_type(text)[0],
            "confidence": RuleBasedExtractor.extract_valve_type(text)[1],
        }
        
        results["parameters"]["class_rating"] = {
            "value": RuleBasedExtractor.extract_class_rating(text)[0],
            "confidence": RuleBasedExtractor.extract_class_rating(text)[1],
        }
        
        results["parameters"]["body_material"] = {
            "value": RuleBasedExtractor.extract_material(text, "body_materials")[0],
            "confidence": RuleBasedExtractor.extract_material(text, "body_materials")[1],
        }
        
        results["parameters"]["trim_material"] = {
            "value": RuleBasedExtractor.extract_material(text, "trim_materials")[0],
            "confidence": RuleBasedExtractor.extract_material(text, "trim_materials")[1],
        }
        
        results["parameters"]["seat_material"] = {
            "value": RuleBasedExtractor.extract_material(text, "seat_materials")[0],
            "confidence": RuleBasedExtractor.extract_material(text, "seat_materials")[1],
        }
        
        results["parameters"]["port_size"] = {
            "value": RuleBasedExtractor.extract_valve_size(text)[0],  # Reuse valve_size logic
            "confidence": RuleBasedExtractor.extract_valve_size(text)[1],
        }
        
        # Extract from tables
        if tables:
            for table in tables:
                if isinstance(table, dict) and "data" in table:
                    table_data = table["data"]
                    # Attempt parameter extraction from table
                    failure_pos, conf = RuleBasedExtractor.extract_from_table(
                        table_data, "failure_position"
                    )
                    if failure_pos:
                        results["parameters"]["failure_position"] = {
                            "value": failure_pos,
                            "confidence": conf,
                        }
        
        # Default values for parameters not extracted
        for param in PARAMETERS_TO_EXTRACT:
            if param not in results["parameters"]:
                results["parameters"][param] = {
                    "value": None,
                    "confidence": 0.0,
                }
        
        logger.info(f"Rule-based extraction completed - Extracted {sum(1 for p in results['parameters'].values() if p['value'])} parameters")
        return results


if __name__ == "__main__":
    # Example usage
    sample_text = """
    TAG: SV-101
    Valve Size: 25 mm
    Valve Type: Globe
    Class Rating: ANSI 150
    Body Material: Carbon Steel
    """
    
    extractor = RuleBasedExtractor()
    results = extractor.extract_all_parameters(sample_text, [])
    print(results)