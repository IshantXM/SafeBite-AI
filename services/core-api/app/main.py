import io
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import inspections_router, analytics_router, rules_router, auth_router
from app.services.safebite_engine import analyze_package_compliance, generate_pdf_report, run_paddle_ocr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CoreAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title="SafetyBite-AI Core API",
    description="Legal Metrology Compliance Verification & Enforcement API - Ministry of Consumer Affairs, Govt of India",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production origins configured in settings.BACKEND_CORS_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(inspections_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(rules_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe for container orchestrator."""
    return {
        "status": "HEALTHY",
        "service": "core-api",
        "version": "1.0.0",
        "doca_compliance": "Legal Metrology Act 2009 & PCR 2011"
    }


@app.post(f"{settings.API_V1_STR}/scan-verify", tags=["Scan Verification"])
async def scan_verify(file: UploadFile = File(...)):
    """Process a package image with OCR and SafeBite compliance analysis, returning a structured verdict and PDF path."""
    try:
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        try:
            ocr_results = run_paddle_ocr(contents)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        analysis = analyze_package_compliance(contents, ocr_results)

        report_dir = Path("/tmp") if Path("/tmp").exists() else Path(".")
        report_name = f"safebite_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        report_path = str(report_dir / report_name)
        generate_pdf_report(analysis, report_path)

        return {
            "success": True,
            "scan_metadata": analysis["scan_metadata"],
            "reasoning_summary": analysis["reasoning_summary"],
            "findings": analysis["findings"],
            "pdf_report_data": analysis["pdf_report_data"],
            "report_url": report_path,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("SafeBite scan verification failed")
        raise HTTPException(status_code=500, detail=f"Scan verification failed: {exc}") from exc
