import io
import logging
import os
import uuid
from datetime import datetime
import cv2
import numpy as np
import requests
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.config import worker_settings
from app.pipeline import (
    ContrastChecker,
    ImagePreprocessor,
    MetricSpatialCalibrator,
    NERClassifier,
    OCREngine,
    RegionDetector,
    StatutoryRuleValidator,
)

logger = logging.getLogger("AITaskWorker")

# Initialize pipeline instances once per worker process
preprocessor = ImagePreprocessor(clip_limit=worker_settings.CLAHE_CLIP_LIMIT, tile_grid_size=(8, 8))
region_detector = RegionDetector(model_path=worker_settings.YOLO_MODEL_PATH)
ocr_engine = OCREngine(lang=worker_settings.PADDLE_OCR_LANG)
ner_classifier = NERClassifier(model_name=worker_settings.SPACY_MODEL)
calibrator = MetricSpatialCalibrator(nominal_barcode_width_mm=worker_settings.EAN13_NOMINAL_WIDTH_MM)
contrast_checker = ContrastChecker()
validator = StatutoryRuleValidator(rules_json_path=worker_settings.RULES_JSON_PATH)

# Database sync engine for worker tasks
db_engine = None
try:
    db_engine = create_engine(worker_settings.DATABASE_SYNC_URL, pool_pre_ping=True)
except Exception as e:
    logger.warning(f"Could not connect to PostgreSQL sync engine: {e}")


def load_image_from_url_or_path(image_source: str) -> np.ndarray:
    """Fetches image from HTTP/S3 URL or local path into OpenCV BGR numpy array."""
    if image_source.startswith("http://") or image_source.startswith("https://"):
        resp = requests.get(image_source, timeout=15)
        resp.raise_for_status()
        image_bytes = np.frombuffer(resp.content, np.uint8)
        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    elif os.path.exists(image_source):
        img = cv2.imread(image_source)
    else:
        # Generate synthetic packaging panel for testing/simulation
        img = np.ones((800, 600, 3), dtype=np.uint8) * 240
        cv2.putText(img, "LMS SAMPLE TEST PACKAGING", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)
        cv2.rectangle(img, (400, 650), (550, 750), (10, 10, 10), -1)  # barcode simulation
    return img


@celery_app.task(bind=True, name="app.tasks.process_inspection_task", max_retries=3)
def process_inspection_task(self, inspection_id_str: str):
    """
    Asynchronous Celery Task:
    Executes end-to-end AI vision and statutory compliance analysis on all panels of an inspection.
    """
    logger.info(f"Starting AI compliance pipeline for inspection: {inspection_id_str}")
    inspection_uuid = uuid.UUID(inspection_id_str)

    if not db_engine:
        logger.error("No database connection available in worker")
        return {"status": "FAILED", "error": "Database unavailable"}

    with Session(db_engine) as session:
        try:
            # Query inspection and panels directly via raw SQL / reflection for robust sync execution
            insp_row = session.execute(
                select(
                    "id", "brand_name", "barcode", "status"
                ).select_from("inspections").where("id" == inspection_uuid)
            ).first()

            panels = session.execute(
                select("id", "panel_type", "raw_image_url")
                .select_from("inspection_panels")
                .where("inspection_id" == inspection_uuid)
            ).all()

            all_violations = []

            for p_id, p_type, raw_url in panels:
                logger.info(f"Processing panel {p_id} ({p_type})")
                img = load_image_from_url_or_path(raw_url)

                # 1. Image Preprocessing (CLAHE, Deskew, Binarize)
                deskewed_img, binarized_img, skew_angle = preprocessor.process(img)

                # 2. Region & Overlapping Sticker Detection (YOLOv8)
                regions = region_detector.detect_regions(deskewed_img)
                barcode_region = regions.get("barcode")
                pdp_region = regions.get("pdp")
                tamper_stickers = regions.get("tamper_stickers", [])

                # 3. Barcode Metric Calibration (mm/px ratio & PDP area)
                scale_ratio = calibrator.calculate_scale_ratio(barcode_region)
                pdp_area_cm2 = calibrator.calculate_pdp_area_cm2(pdp_region, scale_ratio)

                # 4. Multilingual OCR Extraction (PaddleOCR v4)
                ocr_tokens = ocr_engine.extract_text(deskewed_img)

                # 5. Named Entity Classification (spaCy + Regex)
                classified_fields = ner_classifier.classify_tokens(ocr_tokens)

                # 6. Physical Font Height (mm) & WCAG 2.1 Contrast Ratio calculation
                for field_key, f_data in classified_fields.items():
                    height_px = f_data.get("height_px", 20.0)
                    font_mm = calibrator.measure_font_height_mm(height_px, scale_ratio)
                    f_data["measured_font_height_mm"] = font_mm

                    contrast = contrast_checker.calculate_contrast_ratio(deskewed_img, f_data.get("bbox", [0, 0, 10, 10]))
                    f_data["contrast_ratio"] = contrast

                    # Insert detected field record
                    field_id = uuid.uuid4()
                    session.execute(
                        """
                        INSERT INTO detected_fields 
                        (id, panel_id, field_key, extracted_value, confidence, bbox_coordinates, measured_font_height_mm, contrast_ratio)
                        VALUES (:id, :panel_id, :field_key, :extracted_value, :confidence, CAST(:bbox_coordinates AS jsonb), :measured_font_height_mm, :contrast_ratio)
                        """,
                        {
                            "id": field_id,
                            "panel_id": p_id,
                            "field_key": field_key,
                            "extracted_value": f_data.get("extracted_value"),
                            "confidence": f_data.get("confidence"),
                            "bbox_coordinates": json.dumps({"bbox": f_data.get("bbox"), "polygon": f_data.get("polygon")}),
                            "measured_font_height_mm": font_mm,
                            "contrast_ratio": contrast
                        }
                    )

                # Update panel calibration ratio
                session.execute(
                    """
                    UPDATE inspection_panels
                    SET calibration_ratio_px_mm = :ratio
                    WHERE id = :panel_id
                    """,
                    {"ratio": scale_ratio, "panel_id": p_id}
                )

                # 7. Statutory Rule Validation (Rule 6(1)(a)-(f), Rule 7 font table, penalties)
                panel_violations = validator.validate(
                    detected_fields=classified_fields,
                    pdp_area_cm2=pdp_area_cm2,
                    tamper_stickers=tamper_stickers,
                    scale_ratio=scale_ratio
                )
                all_violations.extend(panel_violations)

            # Record violations in database
            for v in all_violations:
                v_id = uuid.uuid4()
                session.execute(
                    """
                    INSERT INTO violations
                    (id, inspection_id, rule_id, clause_reference, description, severity, ai_detected, human_override, penalty_amount, status, created_at, updated_at)
                    VALUES (:id, :inspection_id, :rule_id, :clause_reference, :description, :severity, true, false, :penalty_amount, 'ACTIVE', NOW(), NOW())
                    """,
                    {
                        "id": v_id,
                        "inspection_id": inspection_uuid,
                        "rule_id": v["rule_id"],
                        "clause_reference": v["clause_reference"],
                        "description": v["description"],
                        "severity": v["severity"],
                        "penalty_amount": v["penalty_amount"]
                    }
                )

            # Update overall inspection status
            new_status = "FLAGGED" if len(all_violations) > 0 else "COMPLIANT"
            session.execute(
                """
                UPDATE inspections
                SET status = :status, updated_at = NOW()
                WHERE id = :inspection_id
                """,
                {"status": new_status, "inspection_id": inspection_uuid}
            )

            # Append audit log
            session.execute(
                """
                INSERT INTO audit_logs (entity_type, entity_id, action, executed_by, payload_diff, timestamp)
                VALUES ('INSPECTION', :inspection_id, 'AI_INFERENCE_COMPLETED', '00000000-0000-0000-0000-000000000000', CAST(:payload AS jsonb), NOW())
                """,
                {
                    "inspection_id": inspection_uuid,
                    "payload": json.dumps({"status": new_status, "violations_detected": len(all_violations)})
                }
            )

            session.commit()
            logger.info(f"AI inspection complete for {inspection_id_str}: {new_status} with {len(all_violations)} violations.")
            return {"status": "SUCCESS", "inspection_status": new_status, "violations_count": len(all_violations)}

        except Exception as exc:
            session.rollback()
            logger.error(f"Error during AI pipeline processing for {inspection_id_str}: {exc}")
            raise self.retry(exc=exc, countdown=10)
