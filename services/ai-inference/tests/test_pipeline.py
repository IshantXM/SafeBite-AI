import pytest
import numpy as np
from app.pipeline.font_calibrator import MetricSpatialCalibrator
from app.pipeline.contrast_checker import ContrastChecker
from app.pipeline.validator import StatutoryRuleValidator


def test_font_calibrator_scale_ratio():
    calibrator = MetricSpatialCalibrator(nominal_barcode_width_mm=37.29)
    # 455 pixels width for standard EAN-13
    barcode_region = {"bbox": [100, 100, 455, 120]}
    ratio = calibrator.calculate_scale_ratio(barcode_region)

    assert round(ratio, 4) == round(37.29 / 455.0, 4)
    # Convert a 30px glyph height
    font_mm = calibrator.measure_font_height_mm(30.0, ratio)
    assert font_mm > 2.0


def test_contrast_checker():
    checker = ContrastChecker()
    # High contrast: Black on White
    white = (255.0, 255.0, 255.0)
    black = (0.0, 0.0, 0.0)
    l_white = checker.calculate_relative_luminance(white)
    l_black = checker.calculate_relative_luminance(black)
    contrast = (l_white + 0.05) / (l_black + 0.05)

    assert contrast >= 20.0  # Max contrast ~21:1


def test_statutory_validator_prohibited_qualifier():
    validator = StatutoryRuleValidator()
    fields = {
        "MANUFACTURER_NAME_ADDRESS": {"extracted_value": "Hindustan Packaged Commodities Ltd, New Delhi 110020"},
        "NET_QUANTITY": {"extracted_value": "Net Wt: 500 g approx."},
        "MAXIMUM_RETAIL_PRICE": {"extracted_value": "MRP Rs. 99.00 inclusive of all taxes", "measured_font_height_mm": 2.5},
        "MFG_DATE": {"extracted_value": "08/2026"},
        "CONSUMER_CARE": {"extracted_value": "1800-11-2233 / care@example.com"}
    }
    violations = validator.validate(
        detected_fields=fields,
        pdp_area_cm2=120.0,
        tamper_stickers=[],
        scale_ratio=0.082
    )

    rule_ids = [v["rule_id"] for v in violations]
    assert "LM_RULE_6_1_B_PROHIBITED_QUALIFIER" in rule_ids


def test_statutory_validator_missing_tax_phrase():
    validator = StatutoryRuleValidator()
    fields = {
        "MANUFACTURER_NAME_ADDRESS": {"extracted_value": "Apex Consumer Goods Ltd, Mumbai 400001"},
        "NET_QUANTITY": {"extracted_value": "500 g", "measured_font_height_mm": 2.5},
        "MAXIMUM_RETAIL_PRICE": {"extracted_value": "MRP Rs. 140.00", "measured_font_height_mm": 2.5},  # Missing tax statement
        "MFG_DATE": {"extracted_value": "07/2026"},
        "CONSUMER_CARE": {"extracted_value": "customercare@apex.in"}
    }
    violations = validator.validate(
        detected_fields=fields,
        pdp_area_cm2=150.0,
        tamper_stickers=[],
        scale_ratio=0.082
    )

    rule_ids = [v["rule_id"] for v in violations]
    assert "LM_RULE_6_1_C_TAX_PHRASE" in rule_ids


def test_statutory_validator_font_deficit():
    validator = StatutoryRuleValidator()
    fields = {
        "MANUFACTURER_NAME_ADDRESS": {"extracted_value": "Apex Consumer Goods Ltd, Mumbai 400001"},
        "NET_QUANTITY": {"extracted_value": "500 g", "measured_font_height_mm": 1.20},  # Deficit: required 2.0 mm
        "MAXIMUM_RETAIL_PRICE": {"extracted_value": "MRP Rs. 140.00 inclusive of all taxes", "measured_font_height_mm": 1.20},
        "MFG_DATE": {"extracted_value": "07/2026"},
        "CONSUMER_CARE": {"extracted_value": "customercare@apex.in"}
    }
    violations = validator.validate(
        detected_fields=fields,
        pdp_area_cm2=150.0,  # 50 < A <= 200 bracket requires min 2.0 mm for numerals
        tamper_stickers=[],
        scale_ratio=0.082
    )

    rule_ids = [v["rule_id"] for v in violations]
    assert any("FONT_DEFICIT" in r for r in rule_ids)
