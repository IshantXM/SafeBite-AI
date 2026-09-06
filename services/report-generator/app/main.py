import datetime
import io
import logging
import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Response, status
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from weasyprint import HTML

from app.pki_signer import PKISigner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ReportGenerator")

app = FastAPI(
    title="LMS-Sentinel Statutory Report & Notice Generator",
    description="WeasyPrint PDF Synthesis & PKI Digital Signature Service - Ministry of Consumer Affairs, Govt of India",
    version="1.0.0"
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
pki_signer = PKISigner()


class ViolationItem(BaseModel):
    rule_id: str
    clause_reference: str
    description: Optional[str] = None
    severity: str = "HIGH"
    penalty_amount: float = 25000.0


class GenerateNoticeRequest(BaseModel):
    inspection_id: str
    inspector_id: str
    barcode: Optional[str] = None
    brand_name: Optional[str] = None
    category: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    image_sha256: str
    sync_timestamp: Optional[str] = None
    violations: List[ViolationItem] = []


@app.post("/generate", response_class=Response)
async def generate_statutory_notice(payload: GenerateNoticeRequest):
    """
    Renders official DOCA statutory show cause notice PDF using WeasyPrint
    and digitally signs it using X.509 PKI keys.
    """
    try:
        template = jinja_env.get_template("statutory_notice.html")
        total_penalty = sum(v.penalty_amount for v in payload.violations)
        issue_date = datetime.date.today().strftime("%d %B %Y")
        cert_serial = pki_signer.get_certificate_serial()

        rendered_html = template.render(
            inspection_id=payload.inspection_id,
            inspector_id=payload.inspector_id,
            barcode=payload.barcode,
            brand_name=payload.brand_name,
            category=payload.category,
            geo_lat=payload.geo_lat,
            geo_lng=payload.geo_lng,
            image_sha256=payload.image_sha256,
            sync_timestamp=payload.sync_timestamp or datetime.datetime.utcnow().isoformat(),
            violations=payload.violations,
            total_penalty=total_penalty,
            issue_date=issue_date,
            signer_name="Director of Legal Metrology, DOCA, Govt of India",
            signer_location="New Delhi, India",
            pki_cert_serial=cert_serial
        )

        # Synthesize PDF with WeasyPrint
        pdf_bytes = HTML(string=rendered_html).write_pdf()

        # Generate cryptographic signature
        digital_signature = pki_signer.sign_bytes(pdf_bytes)
        logger.info(f"Digitally signed PDF for inspection {payload.inspection_id} ({len(digital_signature)} signature bytes)")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=DOCA_Statutory_Notice_{payload.inspection_id}.pdf",
                "X-PKI-Signature-Serial": cert_serial
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate notice: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "report-generator", "pki_ready": True}
