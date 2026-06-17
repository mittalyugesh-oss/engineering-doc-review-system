"""
Hybrid Comparison Engine
Combines rule-based and ML-based extraction for parameter matching
"""
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz
from logger_config import logger
from config import HYBRID_WEIGHTS, CONFIDENCE_THRESHOLDS


class HybridComparator:
    """Hybrid comparison of extracted parameters"""
    
    @staticmethod
    def normalize_value(value: str) -> str:
        """Normalize value for comparison"""
        if not value:
            return ""
        return str(value).strip().lower().replace(" ", "").replace("-", "")
    
    @staticmethod
    def calculate_hybrid_confidence(
        rule_based_result: Dict,
        ml_based_result: Dict
    ) -> Tuple[Optional[str], float]:
        """
        Calculate hybrid confidence score combining both methods
        
        Args:
            rule_based_result: Result from rule-based extraction
            ml_based_result: Result from ML-based extraction
            
        Returns:
            Tuple of (agreed_value, combined_confidence)
        """
        rb_value = rule_based_result.get("value")
        rb_conf = rule_based_result.get("confidence", 0.0)
        
        ml_value = ml_based_result.get("value")
        ml_conf = ml_based_result.get("confidence", 0.0)
        
        # If both methods agree
        if rb_value and ml_value and HybridComparator.normalize_value(rb_value) == HybridComparator.normalize_value(ml_value):
            combined_conf = (rb_conf * HYBRID_WEIGHTS["rule_based"] + ml_conf * HYBRID_WEIGHTS["ml_based"])
            return rb_value, min(1.0, combined_conf * 1.1)  # Boost confidence for agreement
        
        # If only one method has high confidence
        if rb_conf >= 0.85 and rb_value:
            return rb_value, rb_conf * HYBRID_WEIGHTS["rule_based"]
        
        if ml_conf >= 0.75 and ml_value:
            return ml_value, ml_conf * HYBRID_WEIGHTS["ml_based"]
        
        # Choose higher confidence result
        if rb_conf > ml_conf and rb_value:
            return rb_value, rb_conf * HYBRID_WEIGHTS["rule_based"]
        elif ml_value:
            return ml_value, ml_conf * HYBRID_WEIGHTS["ml_based"]
        
        return None, 0.0
    
    @staticmethod
    def compare_parameters(
        ga_drawing_params: Dict,
        datasheet_params: Dict
    ) -> Dict:
        """
        Compare GA drawing parameters with datasheet parameters
        """
        comparison_results = {
            "total_parameters": len(ga_drawing_params),
            "matches": {},
            "discrepancies": [],
            "missing_in_ga": [],
            "missing_in_datasheet": [],
            "overall_match_score": 0.0,
        }
        
        matched_count = 0
        
        for param_name, ga_value_dict in ga_drawing_params.items():
            ga_value = ga_value_dict.get("value")
            ga_conf = ga_value_dict.get("confidence", 0.0)
            
            ds_value_dict = datasheet_params.get(param_name, {})
            ds_value = ds_value_dict.get("value")
            ds_conf = ds_value_dict.get("confidence", 0.0)
            
            if not ga_value and not ds_value:
                continue
            
            if not ga_value:
                comparison_results["missing_in_ga"].append({
                    "parameter": param_name,
                    "datasheet_value": ds_value,
                    "severity": "high" if ds_conf > 0.80 else "medium",
                })
                continue
            
            if not ds_value:
                comparison_results["missing_in_datasheet"].append({
                    "parameter": param_name,
                    "ga_value": ga_value,
                    "severity": "medium",
                })
                continue
            
            # Compare values
            match_score = HybridComparator._calculate_match_score(ga_value, ds_value)
            
            comparison_results["matches"][param_name] = {
                "ga_value": ga_value,
                "ga_confidence": ga_conf,
                "datasheet_value": ds_value,
                "datasheet_confidence": ds_conf,
                "match_score": match_score,
                "status": "MATCH" if match_score > 0.85 else "MISMATCH",
            }
            
            if match_score > 0.85:
                matched_count += 1
            else:
                comparison_results["discrepancies"].append({
                    "parameter": param_name,
                    "ga_value": ga_value,
                    "datasheet_value": ds_value,
                    "match_score": match_score,
                    "severity": HybridComparator._classify_severity(param_name, match_score),
                })
        
        # Calculate overall match score
        if comparison_results["total_parameters"] > 0:
            comparison_results["overall_match_score"] = (
                matched_count / comparison_results["total_parameters"]
            )
        
        logger.info(f"Comparison completed - {matched_count}/{comparison_results['total_parameters']} parameters matched")
        return comparison_results
    
    @staticmethod
    def _calculate_match_score(value1: str, value2: str) -> float:
        """Calculate similarity score between two values"""
        if not value1 or not value2:
            return 0.0
        
        # Normalize values
        v1 = HybridComparator.normalize_value(value1)
        v2 = HybridComparator.normalize_value(value2)
        
        # Exact match
        if v1 == v2:
            return 1.0
        
        # Fuzzy match
        fuzzy_score = fuzz.token_set_ratio(v1, v2) / 100.0
        
        return fuzzy_score
    
    @staticmethod
    def _classify_severity(parameter: str, match_score: float) -> str:
        """Classify discrepancy severity"""
        critical_params = ["tag_number", "valve_type", "class_rating", "body_material"]
        
        if parameter in critical_params:
            if match_score < 0.50:
                return "critical"
            else:
                return "major"
        
        if match_score < 0.60:
            return "major"
        else:
            return "minor"
    
    @staticmethod
    def generate_recommendations(
        comparison_results: Dict,
        ga_file: str,
        datasheet_file: str
    ) -> List[Dict]:
        """Generate recommendations based on comparison results"""
        recommendations = []
        
        critical_discrepancies = [d for d in comparison_results["discrepancies"] if d["severity"] == "critical"]
        
        if critical_discrepancies:
            recommendations.append({
                "priority": "HIGH",
                "action": "REVIEW_REQUIRED",
                "message": f"Found {len(critical_discrepancies)} critical discrepancies. Manual review recommended.",
                "discrepancies": critical_discrepancies,
            })
        
        if comparison_results["missing_in_ga"]:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "VERIFY_GA",
                "message": f"GA drawing missing {len(comparison_results['missing_in_ga'])} parameters from datasheet.",
                "missing": comparison_results["missing_in_ga"],
            })
        
        if comparison_results["overall_match_score"] < 0.70:
            recommendations.append({
                "priority": "HIGH",
                "action": "REQUEST_REVISION",
                "message": f"Overall match score is {comparison_results['overall_match_score']:.2%}. Request vendor to revise GA drawing.",
            })
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations