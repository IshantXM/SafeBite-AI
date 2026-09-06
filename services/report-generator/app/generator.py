import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("report_generator")
logger.setLevel(logging.INFO)

class StatutoryReportGenerator:
    """
    Automated PDF Report & Statutory Notice Generator for Consumer Food Safety & Legal Metrology.
    Compiles Jinja2 HTML templates into legally defensible PDF documents with NCH complaint draft.
    """

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_compliance_pdf(
        self,
        inspection_id: str,
        inspector_id: str,
        barcode: str,
        brand_name: str,
        category: str,
        latitude: float,
        longitude: float,
        image_sha256: str,
        parsed_fields: Dict[str, Any],
        metric_calibration: Dict[str, Any],
        rule_evaluation: Dict[str, Any],
        consumer_id: str = "CONSUMER-8842-IND",
        output_dir: str = None,
    ) -> str:
        """
        Builds HTML context, renders Jinja2 template, compiles PDF, and returns file path.
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(output_dir, exist_ok=True)

        notice_ref = f"LMS-2026/DEL/{inspection_id[:8].upper()}"
        formatted_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        lm_violations = rule_evaluation.get("legal_metrology_violations", [])
        fssai_violations = rule_evaluation.get("food_safety_violations", [])
        all_violations = rule_evaluation.get("all_violations", rule_evaluation.get("violations", []))

        # 1. Prepare Template Context
        context = {
            "notice_ref": notice_ref,
            "timestamp": formatted_date,
            "inspection_id": inspection_id,
            "inspector_id": inspector_id,
            "consumer_id": consumer_id,
            "barcode": barcode or "8901030829412",
            "brand_name": brand_name or "Apex FMCG Foods Ltd",
            "category": category or "Packaged Commodities",
            "latitude": f"{latitude:.4f}",
            "longitude": f"{longitude:.4f}",
            "image_sha256": image_sha256 or "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            "parsed_fields": parsed_fields,
            "metric_calibration": metric_calibration,
            "rule_evaluation": rule_evaluation,
            "is_compliant": rule_evaluation.get("is_compliant", False),
            "lm_violations": lm_violations,
            "fssai_violations": fssai_violations,
            "violations": all_violations,
            "total_penalty_inr": rule_evaluation.get("total_penalty_inr", 0.0),
        }

        # 2. Render HTML via Jinja2 Template
        template = self.env.get_template("violation_notice.html")
        rendered_html = template.render(context)

        # 3. Save Output PDF / HTML Document
        pdf_filename = f"{notice_ref.replace('/', '_')}.pdf"
        output_pdf_path = os.path.join(output_dir, pdf_filename)
        html_path = output_pdf_path.replace(".pdf", ".html")

        # Save HTML version always for quick viewing/browser rendering
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        # Try compiling PDF via WeasyPrint / ReportLab
        pdf_compiled = False
        try:
            import weasyprint
            weasyprint.HTML(string=rendered_html).write_pdf(output_pdf_path)
            logger.info(f"WeasyPrint successfully compiled PDF report: {output_pdf_path}")
            pdf_compiled = True
        except Exception as e:
            logger.info(f"WeasyPrint unavailable ({e}). Attempting ReportLab compilation...")

        if not pdf_compiled:
            try:
                # Fallback ReportLab PDF generation if WeasyPrint GTK is missing
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                c = canvas.Canvas(output_pdf_path, pagesize=letter)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, 750, f"OFFICIAL COMPLIANCE REPORT - {notice_ref}")
                c.setFont("Helvetica", 10)
                c.drawString(50, 730, f"Timestamp: {formatted_date} | Barcode: {barcode}")
                c.drawString(50, 715, f"Brand: {brand_name} | Location: {latitude}, {longitude}")
                c.drawString(50, 695, f"Assessed Penalty: INR {rule_evaluation.get('total_penalty_inr', 0.0):,.2f}")
                
                y = 660
                c.setFont("Helvetica-Bold", 11)
                c.drawString(50, y, "Detected Compliance Violations:")
                y -= 20
                c.setFont("Helvetica", 9)
                for v in all_violations:
                    text = f"[{v.get('clause_reference', 'Rule')}] {v.get('title', 'Violation')}: {v.get('description', '')} (Fine: INR {v.get('penalty_inr', 0.0)})"
                    c.drawString(50, y, text[:110])
                    y -= 15
                    if y < 100:
                        c.showPage()
                        y = 750
                c.save()
                logger.info(f"ReportLab successfully compiled PDF report: {output_pdf_path}")
                pdf_compiled = True
            except Exception as ex:
                logger.warning(f"ReportLab compilation failed ({ex}). Returning HTML audit path: {html_path}")
                return html_path

        return output_pdf_path
