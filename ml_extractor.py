"""
ML-Based Parameter Extraction Module (40% of Hybrid Approach)
Uses Named Entity Recognition and Semantic Similarity
"""
import spacy
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple, Optional
import numpy as np
from logger_config import logger
from config import ML_CONFIG, MATERIAL_DATABASE, VALVE_TYPES


class MLExtractor:
    """ML-based parameter extraction using NER and embeddings"""
    
    def __init__(self):
        """Initialize ML models"""
        try:
            # Load spaCy model for NER
            self.nlp = spacy.load(ML_CONFIG["spacy_model"])
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning(f"spaCy model not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", ML_CONFIG["spacy_model"]])
            self.nlp = spacy.load(ML_CONFIG["spacy_model"])
        
        # Load sentence transformer for semantic similarity
        self.sentence_transformer = SentenceTransformer(ML_CONFIG["sentence_transformer_model"])
        logger.info(f"Sentence transformer model loaded: {ML_CONFIG['sentence_transformer_model']}")
        
        # Create embedding database for materials
        self.material_embeddings = self._create_material_embeddings()
        self.valve_embeddings = self._create_valve_embeddings()
    
    def _create_material_embeddings(self) -> Dict:
        """Create embeddings for all known materials"""
        embeddings = {}
        
        for material_type, materials in MATERIAL_DATABASE.items():
            embeddings[material_type] = {
                "materials": materials,
                "embeddings": self.sentence_transformer.encode(
                    materials, convert_to_tensor=True
                ),
            }
        
        logger.info(f"Material embeddings created for {len(MATERIAL_DATABASE)} types")
        return embeddings
    
    def _create_valve_embeddings(self) -> Dict:
        """Create embeddings for all known valve types"""
        embeddings = self.sentence_transformer.encode(
            VALVE_TYPES, convert_to_tensor=True
        )
        
        logger.info(f"Valve type embeddings created for {len(VALVE_TYPES)} types")
        return {
            "types": VALVE_TYPES,
            "embeddings": embeddings,
        }
    
    def extract_entities(self, text: str) -> List[Tuple[str, str, int, int]]:
        """Extract named entities using spaCy NER"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append((ent.text, ent.label_, ent.start_char, ent.end_char))
            logger.debug(f"Entity found: '{ent.text}' ({ent.label_})")
        
        return entities
    
    def find_best_material_match(self, query: str, material_type: str) -> Tuple[Optional[str], float]:
        """Find best matching material using semantic similarity"""
        if material_type not in self.material_embeddings:
            return None, 0.0
        
        material_data = self.material_embeddings[material_type]
        query_embedding = self.sentence_transformer.encode(query, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity_scores = util.pytorch_cos_sim(query_embedding, material_data["embeddings"])[0]
        
        # Get best match
        best_idx = np.argmax(similarity_scores)
        best_score = float(similarity_scores[best_idx])
        best_material = material_data["materials"][best_idx]
        
        logger.debug(f"Material match: {query} -> {best_material} (score: {best_score:.2f})")
        
        return best_material if best_score > 0.5 else None, max(0, best_score - 0.15)
    
    def find_best_valve_type(self, query: str) -> Tuple[Optional[str], float]:
        """Find best matching valve type using semantic similarity"""
        query_embedding = self.sentence_transformer.encode(query, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity_scores = util.pytorch_cos_sim(query_embedding, self.valve_embeddings["embeddings"])[0]
        
        # Get best match
        best_idx = np.argmax(similarity_scores)
        best_score = float(similarity_scores[best_idx])
        best_valve = self.valve_embeddings["types"][best_idx]
        
        logger.debug(f"Valve type match: {query} -> {best_valve} (score: {best_score:.2f})")
        
        return best_valve if best_score > 0.6 else None, max(0, best_score - 0.10)
    
    def extract_all_parameters_ml(self, text: str, tables: List[Dict]) -> Dict:
        """Extract all parameters using ML methods"""
        results = {
            "extraction_method": "ml_based",
            "parameters": {},
        }
        
        # Extract entities first
        entities = self.extract_entities(text)
        
        # Extract each parameter
        results["parameters"]["tag_number"] = self._extract_tag_number_ml(text, entities)
        results["parameters"]["valve_size"] = self._extract_valve_size_ml(text, entities)
        results["parameters"]["valve_type"] = self._extract_valve_type_ml(text, entities)
        results["parameters"]["class_rating"] = self._extract_class_rating_ml(text, entities)
        results["parameters"]["body_material"] = self._extract_body_material_ml(text, entities)
        results["parameters"]["trim_material"] = self._extract_trim_material_ml(text, entities)
        results["parameters"]["seat_material"] = self._extract_seat_material_ml(text, entities)
        results["parameters"]["failure_position"] = self._extract_failure_position_ml(text, entities)
        results["parameters"]["bonnet_type"] = self._extract_bonnet_type_ml(text, entities)
        results["parameters"]["port_size"] = self._extract_port_size_ml(text, entities)
        results["parameters"]["connection_type"] = self._extract_connection_type_ml(text, entities)
        
        logger.info(f"ML-based extraction completed")
        return results
    
    def _extract_tag_number_ml(self, text: str, entities: List) -> Dict:
        """Extract tag number using NER"""
        for entity_text, label, start, end in entities:
            if label in ["PRODUCT", "ORG"] and any(c.isdigit() for c in entity_text):
                return {"value": entity_text, "confidence": 0.75}
        return {"value": None, "confidence": 0.0}
    
    def _extract_valve_size_ml(self, text: str, entities: List) -> Dict:
        """Extract valve size using NER"""
        for entity_text, label, start, end in entities:
            if label == "QUANTITY":
                try:
                    value = float(entity_text)
                    return {"value": str(value), "confidence": 0.70}
                except:
                    pass
        return {"value": None, "confidence": 0.0}
    
    def _extract_valve_type_ml(self, text: str, entities: List) -> Dict:
        """Extract valve type using semantic matching"""
        import re
        valve_keywords = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        for keyword in valve_keywords:
            valve_type, confidence = self.find_best_valve_type(keyword)
            if valve_type and confidence > 0.65:
                return {"value": valve_type, "confidence": confidence}
        
        return {"value": None, "confidence": 0.0}
    
    def _extract_class_rating_ml(self, text: str, entities: List) -> Dict:
        """Extract class rating"""
        for entity_text, label, start, end in entities:
            if any(keyword in entity_text.upper() for keyword in ["ANSI", "DIN", "JIS", "150", "300", "600"]):
                return {"value": entity_text, "confidence": 0.80}
        return {"value": None, "confidence": 0.0}
    
    def _extract_body_material_ml(self, text: str, entities: List) -> Dict:
        """Extract body material"""
        for entity_text, label, start, end in entities:
            if label == "PRODUCT":
                material, confidence = self.find_best_material_match(entity_text, "body_materials")
                if material and confidence > 0.55:
                    return {"value": material, "confidence": confidence}
        return {"value": None, "confidence": 0.0}
    
    def _extract_trim_material_ml(self, text: str, entities: List) -> Dict:
        """Extract trim material"""
        for word in text.split():
            material, confidence = self.find_best_material_match(word, "trim_materials")
            if material and confidence > 0.55:
                return {"value": material, "confidence": confidence}
        return {"value": None, "confidence": 0.0}
    
    def _extract_seat_material_ml(self, text: str, entities: List) -> Dict:
        """Extract seat material"""
        for word in text.split():
            material, confidence = self.find_best_material_match(word, "seat_materials")
            if material and confidence > 0.55:
                return {"value": material, "confidence": confidence}
        return {"value": None, "confidence": 0.0}
    
    def _extract_failure_position_ml(self, text: str, entities: List) -> Dict:
        """Extract failure position"""
        failure_keywords = ["open", "closed", "as-is", "neutral"]
        for keyword in failure_keywords:
            if keyword.lower() in text.lower():
                return {"value": keyword.upper(), "confidence": 0.75}
        return {"value": None, "confidence": 0.0}
    
    def _extract_bonnet_type_ml(self, text: str, entities: List) -> Dict:
        """Extract bonnet type"""
        bonnet_types = ["union", "bolted", "welded", "threaded", "flanged"]
        for bonnet_type in bonnet_types:
            if bonnet_type.lower() in text.lower():
                return {"value": bonnet_type.upper(), "confidence": 0.78}
        return {"value": None, "confidence": 0.0}
    
    def _extract_port_size_ml(self, text: str, entities: List) -> Dict:
        """Extract port size"""
        return self._extract_valve_size_ml(text, entities)
    
    def _extract_connection_type_ml(self, text: str, entities: List) -> Dict:
        """Extract connection type"""
        connection_types = ["NPT", "BSPP", "BSPT", "SAE", "flanged", "threaded"]
        for conn_type in connection_types:
            if conn_type.upper() in text.upper():
                return {"value": conn_type.upper(), "confidence": 0.80}
        return {"value": None, "confidence": 0.0}