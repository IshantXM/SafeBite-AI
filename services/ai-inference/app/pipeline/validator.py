import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Validator")


class StatutoryRuleValidator:
    """
    Production Dual Statutory Rule Engine evaluating against:
    1. Legal Metrology (Packaged Commodities) Rules, 2011 (v2.4) & LM Act, 2009
    2. FSSAI (Labelling and Display) Regulations, 2020
    """

    def __init__(
        self,
        lm_rules_path: Optional[str] = None,
        fssai_rules_path: Optional[str] = None
    ):
        self.lm_rules = self._load_json(lm_rules_path, "LM_PC_RULES_2011_v2.4.json")
        self.fssai_rules = self._load_json(fssai_rules_path, "FSSAI_LABEL_REGULATIONS_2020.json")

    def _load_json(self, path: Optional[str], filename: str) -> Dict[str, Any]:
        target_path = path or os.path.join(os.path.dirname(__file__), "..", "..", "..", "rules", filename)
        if os.path.exists(target_path):
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    logger.info(f"Loaded statutory rules schema from {target_path}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read rules JSON at {target_path}: {e}")
        return {}

    def validate_dual_rules(
        self,
        detected_fields: Dict[str, Dict[str, Any]],
        food_safety_fields: Dict[str, Any],
        veg_symbol_info: Dict[str, Any],
        pdp_area_cm2: float = 150.0,
        tamper_stickers: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Executes dual statutory evaluation across Legal Metrology and FSSAI rules.
        """
        lm_violations = []
        fssai_violations = []

        # =========================================================================
        # 1. LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011 EVALUATION
        # =========================================================================

        # Rule 6(1)(a): Manufacturer / Packer Name & Complete Postal Address
        mfg = detected_fields.get("MANUFACTURER_NAME_ADDRESS", {})
        if not mfg or not mfg.get("extracted_value"):
            lm_violations.append({
                "rule_id": "LM_RULE_6_1_A",
                "clause_reference": "Rule 6(1)(a)",
                "title": "Manufacturer Address Declaration Missing",
                "description": "Missing mandatory declaration of complete name and postal address of manufacturer / packer / importer.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Name & full postal address with pincode",
                "severity": "CRITICAL",
                "penalty_inr": 25000.0,
                "category": "Legal Metrology"
            })

        # Rule 6(1)(b): Net Quantity SI Units & Prohibited Qualifiers
        net_qty = detected_fields.get("NET_QUANTITY", {})
        if not net_qty or not net_qty.get("extracted_value"):
            lm_violations.append({
                "rule_id": "LM_RULE_6_1_B_MISSING",
                "clause_reference": "Rule 6(1)(b)",
                "title": "Net Quantity Missing",
                "description": "Missing mandatory Net Quantity declaration on Principal Display Panel.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Net quantity in legal SI units (g, kg, ml, l, N, U)",
                "severity": "CRITICAL",
                "penalty_inr": 25000.0,
                "category": "Legal Metrology"
            })
        else:
            net_val = net_qty.get("extracted_value", "").lower()
            prohibited = ["approx", "approximate", "when packed", "jumbo", "family size", "extra large", "around"]
            for term in prohibited:
                if term in net_val:
                    lm_violations.append({
                        "rule_id": "LM_RULE_6_1_B_PROHIBITED_QUALIFIER",
                        "clause_reference": "Rule 6(1)(b)",
                        "title": "Prohibited Net Quantity Qualifier",
                        "description": f"Use of prohibited non-standard qualifier '{term}' in Net Quantity declaration.",
                        "observed_value": net_val,
                        "mandated_threshold": "Unqualified exact net quantity",
                        "severity": "HIGH",
                        "penalty_inr": 25000.0,
                        "category": "Legal Metrology"
                    })
                    break

        # Rule 6(1)(c): Maximum Retail Price (MRP) & Tax Inclusivity Phrase
        mrp = detected_fields.get("MAXIMUM_RETAIL_PRICE", {})
        if not mrp or not mrp.get("extracted_value"):
            lm_violations.append({
                "rule_id": "LM_RULE_6_1_C_MISSING",
                "clause_reference": "Rule 6(1)(c)",
                "title": "MRP Declaration Missing",
                "description": "Missing mandatory Maximum Retail Price (MRP) declaration in INR format.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "MRP ₹ XX.XX (inclusive of all taxes)",
                "severity": "CRITICAL",
                "penalty_inr": 25000.0,
                "category": "Legal Metrology"
            })
        else:
            mrp_text = mrp.get("extracted_value", "").lower()
            tax_phrases = ["inclusive of all taxes", "incl. of all taxes", "incl of all taxes", "incl. all taxes"]
            if not any(tp in mrp_text for tp in tax_phrases):
                lm_violations.append({
                    "rule_id": "LM_RULE_6_1_C_TAX_PHRASE",
                    "clause_reference": "Rule 6(1)(c)",
                    "title": "Mandatory Tax Inclusivity Phrase Missing",
                    "description": "MRP declaration fails to state mandatory statutory phrase 'inclusive of all taxes'.",
                    "observed_value": mrp.get("extracted_value"),
                    "mandated_threshold": "Must state 'inclusive of all taxes' or 'incl. of all taxes' adjacent to price",
                    "severity": "CRITICAL",
                    "penalty_inr": 25000.0,
                    "category": "Legal Metrology"
                })

        # Rule 6(1)(d): Month & Year of Manufacture / Packing
        if "MFG_DATE" not in detected_fields or not detected_fields["MFG_DATE"].get("extracted_value"):
            lm_violations.append({
                "rule_id": "LM_RULE_6_1_D_DATE",
                "clause_reference": "Rule 6(1)(d)",
                "title": "Manufacturing Date Missing",
                "description": "Missing declaration of month and year of manufacture or pre-packing.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Month & Year (MM/YYYY) of manufacture or pre-packing",
                "severity": "HIGH",
                "penalty_inr": 25000.0,
                "category": "Legal Metrology"
            })

        # Rule 6(1)(e): Consumer Care Details
        if "CONSUMER_CARE" not in detected_fields or not detected_fields["CONSUMER_CARE"].get("extracted_value"):
            lm_violations.append({
                "rule_id": "LM_RULE_6_1_E_CONSUMER_CARE",
                "clause_reference": "Rule 6(1)(e)",
                "title": "Consumer Care Redressal Details Missing",
                "description": "Missing mandatory consumer care helpline number, email or postal address.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Helpline phone number, email, and address for consumer grievances",
                "severity": "HIGH",
                "penalty_inr": 25000.0,
                "category": "Legal Metrology"
            })

        # Rule 7 & Schedule II: Minimum Font Height Threshold vs PDP Surface Area
        min_required_numeral_mm = 2.0
        if pdp_area_cm2 <= 50:
            min_required_numeral_mm = 1.0
        elif 50 < pdp_area_cm2 <= 200:
            min_required_numeral_mm = 2.0
        elif 200 < pdp_area_cm2 <= 1000:
            min_required_numeral_mm = 4.0
        else:
            min_required_numeral_mm = 6.0

        for key in ["NET_QUANTITY", "MAXIMUM_RETAIL_PRICE"]:
            if key in detected_fields and "height_mm" in detected_fields[key]:
                measured_mm = detected_fields[key]["height_mm"]
                if measured_mm < min_required_numeral_mm:
                    lm_violations.append({
                        "rule_id": f"LM_SCHEDULE_II_{key}_FONT_DEFICIT",
                        "clause_reference": "Rule 7 / Schedule II",
                        "title": f"PDP Font Height Deficit on {key.replace('_', ' ').title()}",
                        "description": f"Measured font height ({measured_mm:.2f} mm) is non-compliant with statutory minimum ({min_required_numeral_mm:.1f} mm).",
                        "observed_value": f"{measured_mm:.2f} mm",
                        "mandated_threshold": f">= {min_required_numeral_mm:.1f} mm for PDP area {pdp_area_cm2:.1f} cm²",
                        "severity": "HIGH",
                        "penalty_inr": 25000.0,
                        "category": "Legal Metrology"
                    })

        # Tamper Detection Sticker Overlay
        if tamper_stickers:
            for sticker in tamper_stickers:
                lm_violations.append({
                    "rule_id": "LM_RULE_TAMPER_STICKER",
                    "clause_reference": "Rule 6 & Section 36",
                    "title": "Tamper Sticker Overlay Detected",
                    "description": "Suspect adhesive sticker overlay detected concealing underlying printed statutory price declaration.",
                    "observed_value": "Sticker Overlay Present",
                    "mandated_threshold": "No adhesive overlays concealing declarations allowed",
                    "severity": "CRITICAL",
                    "penalty_inr": 50000.0,
                    "category": "Legal Metrology"
                })

        # =========================================================================
        # 2. FSSAI (LABELLING AND DISPLAY) REGULATIONS, 2020 EVALUATION
        # =========================================================================

        # FSSAI License Validation (Mandatory 14 Digits)
        fssai_no = detected_fields.get("FSSAI_NO", {})
        if not fssai_no or not fssai_no.get("extracted_value"):
            fssai_violations.append({
                "rule_id": "FSSAI_LICENSE_MISSING",
                "clause_reference": "FSSAI Reg 5(1)",
                "title": "FSSAI Logo & License Number Missing",
                "description": "Missing mandatory FSSAI logo and 14-digit license/registration number.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Valid 14-digit numeric FSSAI License Number",
                "severity": "CRITICAL",
                "penalty_inr": 30000.0,
                "category": "Food Safety"
            })
        else:
            digits_only = re.sub(r'[^0-9]', '', fssai_no.get("extracted_value", ""))
            if len(digits_only) != 14:
                fssai_violations.append({
                    "rule_id": "FSSAI_LICENSE_INVALID_DIGITS",
                    "clause_reference": "FSSAI Reg 5(1)",
                    "title": "Invalid FSSAI License Format",
                    "description": f"FSSAI license number has {len(digits_only)} digits; mandatory 14 digits required.",
                    "observed_value": fssai_no.get("extracted_value"),
                    "mandated_threshold": "Exactly 14 numeric digits",
                    "severity": "CRITICAL",
                    "penalty_inr": 30000.0,
                    "category": "Food Safety"
                })

        # FSSAI Veg / Non-Veg Logo Check
        if not veg_symbol_info or not veg_symbol_info.get("symbol_found"):
            fssai_violations.append({
                "rule_id": "FSSAI_VEG_NON_VEG_MISSING",
                "clause_reference": "FSSAI Reg 5(4)",
                "title": "Dietary Veg / Non-Veg Logo Missing",
                "description": "Missing mandatory vegetarian (green circle) or non-vegetarian (brown triangle) dietary logo.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Green filled circle or Brown filled triangle inside square border",
                "severity": "CRITICAL",
                "penalty_inr": 25000.0,
                "category": "Food Safety"
            })

        # Mandatory Allergen Warning Check
        allergens = food_safety_fields.get("allergens_detected", [])
        has_allergen_declaration = "ALLERGEN_WARNING" in detected_fields or "allergen" in json.dumps(food_safety_fields).lower()
        if allergens and not has_allergen_declaration:
            fssai_violations.append({
                "rule_id": "FSSAI_ALLERGEN_WARNING_MISSING",
                "clause_reference": "FSSAI Reg 5(3)",
                "title": "Mandatory Allergen Declaration Deficit",
                "description": f"Recognized allergens detected ({', '.join(allergens)}) without distinct allergen warning statement or bold text.",
                "observed_value": f"Ingredients contain: {', '.join(allergens)}",
                "mandated_threshold": "Distinct bold allergen declaration (e.g., 'Contains Wheat, Soy')",
                "severity": "CRITICAL",
                "penalty_inr": 35000.0,
                "category": "Food Safety"
            })

        # Mandatory 9-Nutrient Panel Completeness Check
        nutritional_panel = food_safety_fields.get("nutritional_panel", {})
        mandatory_9 = ["energy", "protein", "carbohydrates", "total_sugars", "added_sugars", "total_fat", "saturated_fat", "trans_fat", "sodium"]
        missing_nutrients = [n for n in mandatory_9 if n not in nutritional_panel]
        if missing_nutrients:
            fssai_violations.append({
                "rule_id": "FSSAI_NUTRITION_PANEL_INCOMPLETE",
                "clause_reference": "FSSAI Reg 5(5)",
                "title": "Nutritional Panel Incomplete",
                "description": f"Nutritional panel omits mandatory declared nutrients: {', '.join(missing_nutrients).replace('_', ' ')}.",
                "observed_value": f"{len(nutritional_panel)} of 9 nutrients declared",
                "mandated_threshold": "Complete 9-nutrient breakdown per 100g/100ml or serve",
                "severity": "CRITICAL",
                "penalty_inr": 30000.0,
                "category": "Food Safety"
            })

        # Mandatory Expiry / Best Before Date Check
        exp = detected_fields.get("EXP_DATE", {})
        if not exp or not exp.get("extracted_value"):
            fssai_violations.append({
                "rule_id": "FSSAI_EXPIRY_DATE_MISSING",
                "clause_reference": "FSSAI Reg 5(7)",
                "title": "Expiry / Best Before Date Missing",
                "description": "Missing mandatory 'Best Before' or 'Use By' / Expiry date declaration.",
                "observed_value": "NOT DETECTED",
                "mandated_threshold": "Explicit 'Best Before' or 'Use By' date declaration",
                "severity": "CRITICAL",
                "penalty_inr": 40000.0,
                "category": "Food Safety"
            })

        # Aggregate total penalties & violations list
        all_violations = lm_violations + fssai_violations
        total_penalty = sum(v["penalty_inr"] for v in all_violations)

        return {
            "is_compliant": len(all_violations) == 0,
            "total_violations_count": len(all_violations),
            "lm_violations_count": len(lm_violations),
            "fssai_violations_count": len(fssai_violations),
            "total_penalty_inr": total_penalty,
            "legal_metrology_violations": lm_violations,
            "food_safety_violations": fssai_violations,
            "all_violations": all_violations,
        }
