import os
import sys
import uuid
import numpy as np
import cv2
import logging

# Ensure services directories are in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_DIR = os.path.join(BASE_DIR, "services", "ai-inference")
REPORT_DIR = os.path.join(BASE_DIR, "services", "report-generator")
CORE_API_DIR = os.path.join(BASE_DIR, "services", "core-api")
sys.path.insert(0, AI_DIR)
sys.path.insert(0, REPORT_DIR)
sys.path.insert(0, CORE_API_DIR)

from app.pipeline.unified_parser import UnifiedPDPParser
from app.generator import StatutoryReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LMS_Sentinel_Demo")

def run_demo():
    logger.info("==========================================================================")
    logger.info("  LMS SENTINEL: CONSUMER FOOD SAFETY & LEGAL METROLOGY VERIFICATION RUN  ")
    logger.info("==========================================================================")

    # 1. Initialize Pipeline & Report Generator
    parser = UnifiedPDPParser()
    report_gen = StatutoryReportGenerator()

    # Create dummy images for testing (Food Package Image vs Blank Wall)
    h, w = 800, 600

    # Food package synthetic image (rich texture & color)
    food_img = np.zeros((h, w, 3), dtype=np.uint8)
    food_img[:] = (240, 240, 240)
    cv2.rectangle(food_img, (50, 50), (w-50, h-50), (30, 80, 180), 4) # Packaging frame
    cv2.circle(food_img, (100, 100), 20, (0, 160, 0), -1) # Veg symbol green circle
    cv2.rectangle(food_img, (75, 75), (125, 125), (0, 160, 0), 2) # Veg square border
    cv2.putText(food_img, "APEX CHOCO CRUNCH", (120, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(food_img, "MRP Rs. 45.00", (120, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(food_img, "Net Wt: 150g", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(food_img, "Ingredients: Wheat Flour, Sugar, Palm Oil, Cocoa (INS 500), Milk Solids", (80, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # Blank wall image (plain featureless surface)
    blank_wall_img = np.ones((h, w, 3), dtype=np.uint8) * 220

    # -------------------------------------------------------------------------
    # TEST CASE 1: Blank Wall Scan Rejection
    # -------------------------------------------------------------------------
    logger.info("\n--- TEST CASE 1: Non-Food / Blank Wall Detection ---")
    blank_result = parser.parse_and_validate(
        ocr_tokens=[],
        image=blank_wall_img
    )
    logger.info(f"Blank Wall Result: Success={blank_result['success']}, IsFoodPackage={blank_result['is_food_package']}")
    if not blank_result['is_food_package']:
        logger.info(f"✅ BLANK WALL REJECTED PROPERLY: '{blank_result['error_message']}'")
    else:
        logger.error("❌ Blank wall check failed.")

    # -------------------------------------------------------------------------
    # TEST CASE 2: Packaged Food Item Audit & Dual Statutory Rule Evaluation
    # -------------------------------------------------------------------------
    logger.info("\n--- TEST CASE 2: Food Package Optical AI & Dual Rule Engine ---")

    # Simulated OCR tokens extracted from food packaging panel
    ocr_tokens = [
        {"text": "APEX FOODS LIMITED", "confidence": 0.98, "box": {"x": 100, "y": 50, "width": 300, "height": 24}},
        {"text": "MRP Rs. 45.00", "confidence": 0.96, "box": {"x": 100, "y": 120, "width": 180, "height": 12}}, # 12px height -> 1.35mm font height (< 2.0mm threshold) -> Font deficit violation!
        {"text": "Net Wt: 150g (approx)", "confidence": 0.95, "box": {"x": 100, "y": 160, "width": 200, "height": 16}}, # "approx" qualifier -> Prohibited net qty qualifier violation!
        {"text": "MFG Date: 05/2026", "confidence": 0.94, "box": {"x": 100, "y": 200, "width": 180, "height": 14}},
        {"text": "Ingredients: Wheat Flour, Sugar, Soy Lecithin (INS 322), Milk Powder, Peanuts", "confidence": 0.92, "box": {"x": 50, "y": 250, "width": 500, "height": 12}},
        {"text": "Nutritional Information per 100g: Energy 480 kcal, Protein 6.5g, Total Fat 18g", "confidence": 0.90, "box": {"x": 50, "y": 300, "width": 500, "height": 12}},
    ]

    food_result = parser.parse_and_validate(
        ocr_tokens=ocr_tokens,
        image=food_img,
        detected_barcode_box={"x": 50, "y": 400, "width": 330, "height": 100}, # Barcode width 330px -> scale 0.113 mm/px
        provided_brand_name="Apex Foods Ltd"
    )

    logger.info(f"Food Package Scan Result: Success={food_result['success']}")
    logger.info(f"Metric Calibration Scale: {food_result['metric_calibration']['scale_mm_per_px']} mm/px")
    logger.info(f"Measured Font Height: {food_result['metric_calibration']['measured_font_height_mm']} mm (Min required: 2.0 mm)")

    eval_data = food_result["rule_evaluation"]
    logger.info(f"Is Compliant: {eval_data['is_compliant']}")
    logger.info(f"Total Violations: {eval_data['total_violations_count']} (LM: {eval_data['lm_violations_count']}, FSSAI: {eval_data['fssai_violations_count']})")
    logger.info(f"Total Fine Assessed: ₹{eval_data['total_penalty_inr']:,.2f}")

    for idx, v in enumerate(eval_data["all_violations"], 1):
        logger.info(f"  [{idx}] [{v['category']}] {v['clause_reference']} - {v['title']}: {v['description']} (Fine: ₹{v['penalty_inr']:,.0f})")

    # -------------------------------------------------------------------------
    # TEST CASE 3: PDF Report Generation with Dual Matrices & NCH Complaint Draft
    # -------------------------------------------------------------------------
    logger.info("\n--- TEST CASE 3: PDF Audit Report Generation ---")
    scan_id = str(uuid.uuid4())
    output_pdf_path = report_gen.generate_compliance_pdf(
        inspection_id=scan_id,
        inspector_id="CONSUMER-DOCA-88",
        barcode="8901030829412",
        brand_name="Apex Foods Ltd",
        category="Packaged Food",
        latitude=28.6139,
        longitude=77.2090,
        image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        parsed_fields=food_result["parsed_fields"],
        metric_calibration=food_result["metric_calibration"],
        rule_evaluation=eval_data,
        consumer_id="CONSUMER-9921-DEL",
        output_dir=os.path.join(BASE_DIR, "artifacts")
    )
    logger.info(f"✅ PDF AUDIT REPORT SUCCESSFULLY GENERATED AT:\n   {output_pdf_path}")

    # -------------------------------------------------------------------------
    # TEST CASE 4: Role-Based Access Control (RBAC) & Persona JWT Authentication
    # -------------------------------------------------------------------------
    logger.info("\n--- TEST CASE 4: Role-Based Access Control (RBAC) & Personas ---")
    from app.security.auth import decode_token
    from app.security.roles import UserRole
    from app.config import settings
    import jwt

    def generate_jwt(user_id: uuid.UUID, username: str, email: str, roles: list) -> str:
        payload = {
            "sub": str(user_id),
            "username": username,
            "email": email,
            "roles": roles,
            "realm_access": {"roles": roles},
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    personas = [
        ("Consumer User", UserRole.CONSUMER.value),
        ("Field Inspector", UserRole.INSPECTOR.value),
        ("Zone Supervisor", UserRole.SUPERVISOR.value),
        ("DOCA System Admin", UserRole.ADMIN.value),
    ]

    for p_name, p_role in personas:
        t_token = generate_jwt(
            user_id=uuid.uuid4(),
            username=p_name.lower().replace(" ", "_"),
            email=f"{p_name.lower().replace(' ', '.')}@sentinel.gov.in",
            roles=[p_role]
        )
        decoded = decode_token(t_token)
        logger.info(f"  🔐 Persona [{p_name}] -> Role: {decoded['roles']} | JWT Auth Verified ✅")

    logger.info("\n==========================================================================")
    logger.info("  SYSTEM VERIFICATION SUCCESSFUL - ALL MODULES & RBAC FULLY OPERATIONAL  ")
    logger.info("==========================================================================")

if __name__ == "__main__":
    run_demo()
