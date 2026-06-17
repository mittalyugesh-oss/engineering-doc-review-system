"""
Main orchestration script
"""
import argparse
from pathlib import Path
from logger_config import logger
from document_processor import DocumentProcessor
from parameter_extractor import RuleBasedExtractor
from ml_extractor import MLExtractor
from comparator import HybridComparator
from reporter import ReportGenerator


def extract_single_document(file_path: str):
    """Extract parameters from a single document"""
    logger.info(f"Starting extraction for: {file_path}")
    
    # Process
    doc_processor = DocumentProcessor()
    doc_result = doc_processor.process_document(file_path)
    
    if doc_result["status"] != "success":
        logger.error(f"Failed to process document: {doc_result.get('error')}")
        return
    
    # Extract using both methods
    rb_result = RuleBasedExtractor.extract_all_parameters(
        doc_result["text"],
        doc_result["tables"]
    )
    
    ml_extractor = MLExtractor()
    ml_result = ml_extractor.extract_all_parameters_ml(
        doc_result["text"],
        doc_result["tables"]
    )
    
    # Combine using hybrid approach
    comparator = HybridComparator()
    hybrid_params = {}
    
    for param in rb_result["parameters"].keys():
        rb = rb_result["parameters"][param]
        ml = ml_result["parameters"][param]
        value, conf = comparator.calculate_hybrid_confidence(rb, ml)
        hybrid_params[param] = {
            "value": value,
            "confidence": conf,
            "rule_based": rb,
            "ml_based": ml,
        }
    
    # Display results
    print("\n" + "="*60)
    print(f"EXTRACTION RESULTS FOR: {Path(file_path).name}")
    print("="*60)
    
    for param, result in hybrid_params.items():
        print(f"\n{param.upper().replace('_', ' ')}")
        print(f"  Value: {result['value']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Rule-Based: {result['rule_based']['value']} ({result['rule_based']['confidence']:.2%})")
        print(f"  ML-Based: {result['ml_based']['value']} ({result['ml_based']['confidence']:.2%})")
    
    return hybrid_params


def compare_documents(ga_file: str, datasheet_file: str):
    """Compare GA drawing with datasheet"""
    logger.info(f"Starting comparison: {ga_file} vs {datasheet_file}")
    
    # Process both documents
    doc_processor = DocumentProcessor()
    ga_result = doc_processor.process_document(ga_file)
    ds_result = doc_processor.process_document(datasheet_file)
    
    if ga_result["status"] != "success" or ds_result["status"] != "success":
        logger.error("Failed to process documents")
        return
    
    # Extract from GA
    ga_rb = RuleBasedExtractor.extract_all_parameters(ga_result["text"], ga_result["tables"])
    ml_extractor = MLExtractor()
    ga_ml = ml_extractor.extract_all_parameters_ml(ga_result["text"], ga_result["tables"])
    
    # Extract from datasheet
    ds_rb = RuleBasedExtractor.extract_all_parameters(ds_result["text"], ds_result["tables"])
    ds_ml = ml_extractor.extract_all_parameters_ml(ds_result["text"], ds_result["tables"])
    
    # Combine
    comparator = HybridComparator()
    ga_params = {}
    ds_params = {}
    
    for param in ga_rb["parameters"].keys():
        rb = ga_rb["parameters"][param]
        ml = ga_ml["parameters"][param]
        value, conf = comparator.calculate_hybrid_confidence(rb, ml)
        ga_params[param] = {"value": value, "confidence": conf}
        
        rb_ds = ds_rb["parameters"][param]
        ml_ds = ds_ml["parameters"][param]
        value_ds, conf_ds = comparator.calculate_hybrid_confidence(rb_ds, ml_ds)
        ds_params[param] = {"value": value_ds, "confidence": conf_ds}
    
    # Compare
    comparison_results = comparator.compare_parameters(ga_params, ds_params)
    recommendations = comparator.generate_recommendations(
        comparison_results,
        ga_file,
        datasheet_file
    )
    
    # Generate reports
    report_gen = ReportGenerator()
    json_report = report_gen.generate_json_report(
        ga_file,
        datasheet_file,
        ga_params,
        ds_params,
        comparison_results,
        recommendations,
    )
    
    pdf_report = report_gen.generate_pdf_report(
        ga_file,
        datasheet_file,
        comparison_results,
        recommendations,
    )
    
    html_report = report_gen.generate_html_report(
        ga_file,
        datasheet_file,
        comparison_results,
        recommendations,
    )
    
    # Display results
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    print(f"\nOverall Match Score: {comparison_results['overall_match_score']:.2%}")
    print(f"Parameters Matched: {sum(1 for m in comparison_results['matches'].values() if m['status'] == 'MATCH')}")
    print(f"Discrepancies: {len(comparison_results['discrepancies'])}")
    
    if comparison_results["discrepancies"]:
        print("\nDiscrepancies Found:")
        for disc in comparison_results["discrepancies"]:
            print(f"  - {disc['parameter']}: {disc['severity'].upper()}")
            print(f"    GA: {disc['ga_value']}")
            print(f"    Datasheet: {disc['datasheet_value']}")
    
    if recommendations:
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  [{rec['priority']}] {rec['action']}: {rec['message']}")
    
    print(f"\nReports generated:")
    print(f"  JSON: {json_report}")
    print(f"  PDF: {pdf_report}")
    print(f"  HTML: {html_report}")
    
    return comparison_results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Engineering Document Review System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract parameters from document")
    extract_parser.add_argument("file", help="Path to document file")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare GA drawing with datasheet")
    compare_parser.add_argument("ga_file", help="Path to GA drawing")
    compare_parser.add_argument("datasheet_file", help="Path to datasheet")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="API host")
    api_parser.add_argument("--port", type=int, default=8000, help="API port")
    
    # UI command
    ui_parser = subparsers.add_parser("ui", help="Start Streamlit UI")
    
    args = parser.parse_args()
    
    if args.command == "extract":
        extract_single_document(args.file)
    
    elif args.command == "compare":
        compare_documents(args.ga_file, args.datasheet_file)
    
    elif args.command == "api":
        from api import app
        import uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    
    elif args.command == "ui":
        import subprocess
        subprocess.run(["streamlit", "run", "ui.py"])
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()