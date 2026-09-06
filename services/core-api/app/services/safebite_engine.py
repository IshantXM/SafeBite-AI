import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

try:
    from paddleocr import PaddleOCR
except Exception:  # pragma: no cover
    PaddleOCR = None


def run_paddle_ocr(image_bytes: bytes) -> List[Dict[str, Any]]:
    """Run PaddleOCR on the uploaded image and return structured OCR tokens."""
    if PaddleOCR is None:
        raise RuntimeError("PaddleOCR is not installed in the backend environment.")

    image = Image.open(__import__('io').BytesIO(image_bytes)).convert("RGB")
    arr = np.array(image)

    engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    results = engine.ocr(arr, cls=True)

    extracted: List[Dict[str, Any]] = []
    if results and results[0]:
        for line in results[0]:
            if not line or len(line) < 2:
                continue
            coords, text_conf = line
            text_value, conf_value = text_conf
            if not isinstance(text_value, str):
                continue
            polygon = coords if isinstance(coords, list) else []
            extracted.append(
                {
                    "text": text_value.strip(),
                    "confidence": float(conf_value),
                    "polygon": polygon,
                    "bbox": _polygon_to_bbox(polygon),
                }
            )
    return extracted


def _polygon_to_bbox(polygon: List[List[float]]) -> List[int]:
    if not polygon:
        return [0, 0, 0, 0]
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    x_min = int(min(xs))
    y_min = int(min(ys))
    x_max = int(max(xs))
    y_max = int(max(ys))
    return [x_min, y_min, max(0, x_max - x_min), max(0, y_max - y_min)]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def _find_field(text: str, patterns: List[str]) -> Tuple[bool, str]:
    normalized = _normalize_text(text)
    for pattern in patterns:
        if pattern in normalized:
            return True, pattern
    return False, ""


def analyze_package_compliance(image_bytes: bytes, ocr_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    combined = " ".join(item.get("text", "") for item in ocr_results)
    normalized = _normalize_text(combined)

    findings: List[Dict[str, Any]] = []
    score = 100

    def add_finding(field: str, status: str, severity: str, detected_value: str, required_value: str, legal_rule: str, observation: str):
        nonlocal score
        findings.append(
            {
                "field": field,
                "status": status,
                "severity": severity,
                "detected_value": detected_value,
                "required_value": required_value,
                "legal_rule": legal_rule,
                "observation": observation,
            }
        )
        if status == "NON_COMPLIANT":
            score -= 18 if severity in {"HIGH", "CRITICAL"} else 10
        elif status == "NOT_FOUND":
            score -= 12

    label_detected = bool(ocr_results) and bool(normalized)
    if not label_detected:
        return {
            "scan_metadata": {
                "label_detected": False,
                "commodity_type": "Unknown",
                "overall_verdict": "REJECTED",
                "compliance_score_pct": 0,
            },
            "reasoning_summary": "No readable label text or packaging declarations were detected in the uploaded image.",
            "findings": [],
            "pdf_report_data": {
                "inspection_case_id": "CASE-AUTO-GENERATED",
                "digital_signature_hash": "SHA256-READY",
                "action_required": True,
            },
        }

    commodity_type = "Packaged Consumer Commodity"
    if any(key in normalized for key in ["oil", "atta", "rice", "tea", "milk", "salt", "flour", "biscuit", "soap", "detergent", "biscuits"]):
        commodity_type = "Packaged Food / Consumer Commodity"

    # MRP
    mrp_found = bool(re.search(r"mrp|price|rs\.|₹|inclusive of all taxes|incl\.|incl\ of all taxes", normalized))
    if mrp_found:
        add_finding(
            "MRP Declaration",
            "COMPLIANT" if "inclusive of all taxes" in normalized or "incl. of all taxes" in normalized else "NON_COMPLIANT",
            "HIGH" if "inclusive of all taxes" not in normalized else "LOW",
            detected_value="Detected in OCR text",
            required_value="MRP with incl. of all taxes",
            legal_rule="Rule LM-PC-2011-6(1)(c)",
            observation="MRP visibility checked against the packing declaration conditions.",
        )
    else:
        add_finding(
            "MRP Declaration",
            "NOT_FOUND",
            "HIGH",
            detected_value="None",
            required_value="MRP with tax inclusion statement",
            legal_rule="Rule LM-PC-2011-6(1)(c)",
            observation="No MRP declaration was detected in readable text.",
        )

    # Net quantity
    qty_patterns = ["g", "kg", "ml", "l", "litre", "liter", "gram", "grams", "millilitre"]
    qty_found = any(token in normalized for token in ["net quantity", "net wt", "net wt.", "quantity", "net content"])
    if qty_found:
        qty_status = "COMPLIANT"
        qty_sev = "LOW"
        if re.search(r"gms|gms\.|litres|kilos|kgs\.|ml\.|l\.|kg\.", normalized):
            qty_status = "NON_COMPLIANT"
            qty_sev = "MEDIUM"
        add_finding(
            "Net Quantity",
            qty_status,
            qty_sev,
            detected_value="Detected quantity declaration",
            required_value="Standard unit format (g, kg, ml, l, N)",
            legal_rule="Rule LM-PC-2011-6(1)(b)",
            observation="Checked whether the label uses standard legal metrology units without prohibited abbreviations.",
        )
    else:
        add_finding(
            "Net Quantity",
            "NOT_FOUND",
            "HIGH",
            detected_value="None",
            required_value="Net quantity in standard units",
            legal_rule="Rule LM-PC-2011-6(1)(b)",
            observation="No clear net quantity declaration was identified.",
        )

    # manufacturer
    manufacturer_found = bool(re.search(r"manufactur|packer|importer|mfg|packed by|packer|producer", normalized))
    if manufacturer_found:
        add_finding(
            "Manufacturer / Packer Details",
            "COMPLIANT",
            "LOW",
            detected_value="Detected manufacturer or packer details",
            required_value="Name and complete address",
            legal_rule="Rule LM-PC-2011-6(1)(a)",
            observation="Manufacturer or packer traceability text was found in the label.",
        )
    else:
        add_finding(
            "Manufacturer / Packer Details",
            "NOT_FOUND",
            "HIGH",
            detected_value="None",
            required_value="Name and complete address",
            legal_rule="Rule LM-PC-2011-6(1)(a)",
            observation="No full manufacturer or packer details were detected.",
        )

    # date
    date_found = bool(re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)|\d{1,2}/\d{4}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4}", normalized))
    if date_found:
        add_finding(
            "Date of Manufacture / Packaging",
            "COMPLIANT",
            "LOW",
            detected_value="Detected month-year or date text",
            required_value="Month and year or exact date format",
            legal_rule="Rule LM-PC-2011-6(1)(d)",
            observation="Date declaration present and parsed from the OCR output.",
        )
    else:
        add_finding(
            "Date of Manufacture / Packaging",
            "NOT_FOUND",
            "MEDIUM",
            detected_value="None",
            required_value="Month and year declaration",
            legal_rule="Rule LM-PC-2011-6(1)(d)",
            observation="No explicit month/year manufacturing or packing declaration was found.",
        )

    # consumer care
    consumer_care_found = bool(re.search(r"consumer care|grievance|helpline|tel|phone|email|contact|support@|care@", normalized))
    if consumer_care_found:
        add_finding(
            "Consumer Care / Grievance Details",
            "COMPLIANT",
            "LOW",
            detected_value="Detected customer support information",
            required_value="Email or phone number and address",
            legal_rule="Rule LM-PC-2011-6(1)(e)",
            observation="Customer support contact details were detected in visible text.",
        )
    else:
        add_finding(
            "Consumer Care / Grievance Details",
            "NOT_FOUND",
            "MEDIUM",
            detected_value="None",
            required_value="Contact information for consumer redressal",
            legal_rule="Rule LM-PC-2011-6(1)(e)",
            observation="No consumer complaint or support contact details were found.",
        )

    # origin
    origin_found = bool(re.search(r"country of origin|made in|origin|manufactured in|imported from", normalized))
    if origin_found:
        add_finding(
            "Country of Origin",
            "COMPLIANT",
            "LOW",
            detected_value="Detected origin text",
            required_value="Origin country declaration",
            legal_rule="Rule LM-PC-2011-6(1)(f)",
            observation="Country of origin declaration appears in the visible packaging text.",
        )
    else:
        add_finding(
            "Country of Origin",
            "NOT_FOUND",
            "MEDIUM",
            detected_value="None",
            required_value="Mandatory origin country declaration",
            legal_rule="Rule LM-PC-2011-6(1)(f)",
            observation="No country-of-origin declaration was found on the package.",
        )

    # FSSAI for edible
    if any(word in normalized for word in ["food", "oil", "atta", "rice", "milk", "salt", "tea", "biscuits", "snacks"]):
        fssai_found = bool(re.search(r"fssai|license no|lic no|fssai lic|100\d{12}", normalized))
        if fssai_found:
            add_finding(
                "FSSAI License / Food Declaration",
                "COMPLIANT",
                "LOW",
                detected_value="Detected FSSAI marker",
                required_value="14-digit FSSAI license number",
                legal_rule="Rule LM-PC-2011-Food Regulations",
                observation="Food-segment labeling includes FSSAI registration details.",
            )
        else:
            add_finding(
                "FSSAI License / Food Declaration",
                "NOT_FOUND",
                "HIGH",
                detected_value="None",
                required_value="14-digit FSSAI license number",
                legal_rule="Rule LM-PC-2011-Food Regulations",
                observation="Food package appears edible but no FSSAI license or food registration number was detected.",
            )

    violations = [item for item in findings if item["status"] in {"NON_COMPLIANT", "NOT_FOUND"}]
    overall_verdict = "COMPLIANT" if not violations else "NON_COMPLIANT"
    if not label_detected:
        overall_verdict = "REJECTED"

    compliance_score_pct = max(0, min(100, score))
    reasoning_summary = (
        "Statutory label elements were identified but one or more mandatory compliance checks are missing or non-compliant."
        if violations
        else "All inspected declarations were detected and conform to the expected compliance checks."
    )

    return {
        "scan_metadata": {
            "label_detected": label_detected,
            "commodity_type": commodity_type,
            "overall_verdict": overall_verdict,
            "compliance_score_pct": compliance_score_pct,
        },
        "reasoning_summary": reasoning_summary,
        "findings": findings,
        "pdf_report_data": {
            "inspection_case_id": "CASE-AUTO-GENERATED",
            "digital_signature_hash": hashlib.sha256(json.dumps({"ocr": ocr_results, "findings": findings}, sort_keys=True).encode()).hexdigest(),
            "action_required": bool(violations),
        },
    }


def generate_pdf_report(report_data: Dict[str, Any], output_path: str) -> str:
    """Generate a PDF file from the structured compliance report."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_file), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("SafeBite-AI Compliance Report", styles["Title"]))
    story.append(Paragraph(f"Verdict: {report_data['scan_metadata']['overall_verdict']}", styles["Heading2"]))
    story.append(Paragraph(f"Compliance Score: {report_data['scan_metadata']['compliance_score_pct']}%", styles["Normal"]))
    story.append(Paragraph(report_data.get("reasoning_summary", ""), styles["Normal"]))
    story.append(Spacer(1, 12))

    table_data = [["Field", "Status", "Severity", "Rule", "Observation"]]
    for item in report_data.get("findings", []):
        table_data.append([
            item.get("field", ""),
            item.get("status", ""),
            item.get("severity", ""),
            item.get("legal_rule", ""),
            item.get("observation", ""),
        ])

    table = Table(table_data, colWidths=[100, 80, 60, 110, 180])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B4F6C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Digest: {report_data['pdf_report_data']['digital_signature_hash']}", styles["Normal"]))
    doc.build(story)
    return str(output_file)
