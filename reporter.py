"""
Report Generation Module
Generates PDF, JSON, and HTML reports
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from logger_config import logger
from config import RESULTS_DIR


class ReportGenerator:
    """Generate various report formats"""
    
    @staticmethod
    def generate_json_report(
        ga_file: str,
        datasheet_file: str,
        ga_extraction: Dict,
        ds_extraction: Dict,
        comparison_results: Dict,
        recommendations: List[Dict],
        output_path: str = None
    ) -> str:
        """
        Generate JSON report
        """
        if not output_path:
            output_path = str(RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "ga_file": ga_file,
                "datasheet_file": datasheet_file,
            },
            "extraction": {
                "ga_drawing": ga_extraction,
                "datasheet": ds_extraction,
            },
            "comparison": comparison_results,
            "recommendations": recommendations,
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"JSON report generated: {output_path}")
        return output_path
    
    @staticmethod
    def generate_pdf_report(
        ga_file: str,
        datasheet_file: str,
        comparison_results: Dict,
        recommendations: List[Dict],
        output_path: str = None
    ) -> str:
        """
        Generate PDF report
        """
        if not output_path:
            output_path = str(RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30,
        )
        elements.append(Paragraph("Engineering Document Review Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Metadata
        meta_data = [
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["GA Drawing:", ga_file],
            ["Datasheet:", datasheet_file],
        ]
        meta_table = Table(meta_data, colWidths=[150, 350])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))
        
        # Overall Score
        overall_score = comparison_results.get("overall_match_score", 0) * 100
        score_status = "PASS" if overall_score >= 80 else "REVIEW REQUIRED"
        score_color = colors.green if overall_score >= 80 else colors.red
        
        score_para = Paragraph(
            f"<b>Overall Match Score: <font color='{score_color.hexval()}'>{overall_score:.1f}%</font></b>",
            styles['Heading2']
        )
        elements.append(score_para)
        elements.append(Spacer(1, 12))
        
        # Comparison Results Table
        elements.append(Paragraph("Parameter Comparison", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        matches = comparison_results.get("matches", {})
        table_data = [
            ["Parameter", "GA Value", "Datasheet Value", "Match Score", "Status"],
        ]
        
        for param, result in matches.items():
            table_data.append([
                param,
                str(result.get("ga_value", "")),
                str(result.get("datasheet_value", "")),
                f"{result.get('match_score', 0):.2%}",
                result.get("status", ""),
            ])
        
        if len(table_data) > 1:
            comp_table = Table(table_data, colWidths=[120, 100, 100, 100, 80])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(comp_table)
        
        elements.append(Spacer(1, 20))
        
        # Discrepancies
        if comparison_results.get("discrepancies"):
            elements.append(PageBreak())
            elements.append(Paragraph("Discrepancies Found", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            disc_data = [
                ["Parameter", "GA Value", "Datasheet Value", "Severity"],
            ]
            
            for disc in comparison_results["discrepancies"]:
                disc_data.append([
                    disc.get("parameter", ""),
                    str(disc.get("ga_value", "")),
                    str(disc.get("datasheet_value", "")),
                    disc.get("severity", "").upper(),
                ])
            
            disc_table = Table(disc_data, colWidths=[120, 100, 100, 100])
            disc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6666')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(disc_table)
        
        # Recommendations
        if recommendations:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Recommendations", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            for rec in recommendations:
                priority_color = {
                    "HIGH": colors.red,
                    "MEDIUM": colors.orange,
                    "LOW": colors.green,
                }.get(rec.get("priority", "LOW"), colors.black)
                
                rec_para = Paragraph(
                    f"<b><font color='{priority_color.hexval()}'>[{rec.get('priority')}]</font> {rec.get('message', '')}</b>",
                    styles['Normal']
                )
                elements.append(rec_para)
                elements.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(elements)
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    
    @staticmethod
    def generate_html_report(
        ga_file: str,
        datasheet_file: str,
        comparison_results: Dict,
        recommendations: List[Dict],
        output_path: str = None
    ) -> str:
        """
        Generate HTML report
        """
        if not output_path:
            output_path = str(RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        overall_score = comparison_results.get("overall_match_score", 0) * 100
        score_status = "PASS" if overall_score >= 80 else "REVIEW REQUIRED"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Engineering Document Review Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 900px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
                h1 {{ color: #003366; border-bottom: 2px solid #003366; padding-bottom: 10px; }}
                h2 {{ color: #003366; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background-color: #003366; color: white; padding: 12px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .metadata {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .score {{ font-size: 24px; font-weight: bold; color: {'green' if overall_score >= 80 else 'red'}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Engineering Document Review Report</h1>
                <div class="metadata">
                    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>GA Drawing:</strong> {ga_file}</p>
                    <p><strong>Datasheet:</strong> {datasheet_file}</p>
                </div>
                <h2>Overall Assessment</h2>
                <p>Overall Match Score: <span class="score">{overall_score:.1f}%</span></p>
                <p>Status: <strong>{score_status}</strong></p>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report generated: {output_path}")
        return output_path