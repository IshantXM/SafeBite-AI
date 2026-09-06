import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("NERClassifier")

try:
    import spacy
except ImportError:
    spacy = None


class NERClassifier:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = None
        if spacy:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model {model_name}")
            except Exception as e:
                logger.warning(f"Could not load spaCy model {model_name}: {e}. Utilizing deterministic regex NER.")

        # Regex patterns for deterministic extraction
        self.patterns = {
            "NET_QUANTITY": [
                re.compile(r"(?:net\s*(?:qty|quantity|wt|weight|vol|volume)?\s*[:\.-]?\s*)(\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|ml|l|ltr|litres|m|cm|mm|units?|pieces?|N|U))\b", re.IGNORECASE),
                re.compile(r"\b(\d+(?:\.\d+)?\s*(?:kg|g|gm|gms|ml|l|ltr|N|U))\b", re.IGNORECASE)
            ],
            "MAXIMUM_RETAIL_PRICE": [
                re.compile(r"(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price)\s*[:\.-]?\s*(?:(?:rs|inr|₹)\.?\s*)?(\d+(?:\.\d{1,2})?)(.*?)(?=$|\n)", re.IGNORECASE),
                re.compile(r"(?:₹|rs\.?)\s*(\d+(?:\.\d{1,2})?)", re.IGNORECASE)
            ],
            "MFG_DATE": [
                re.compile(r"(?:mfg|mfd|packed|pkd|manufactured|date\s*of\s*(?:packing|mfg))\s*[:\.-]?\s*([0-9]{1,2}[\/\.-][0-9]{2,4}|[A-Za-z]{3,9}\s*[\/\.-]?\s*[0-9]{2,4})", re.IGNORECASE),
                re.compile(r"\b(0[1-9]|1[0-2])[\/\.-](20\d{2}|\d{2})\b")
            ],
            "EXP_DATE": [
                re.compile(r"(?:use\s*by|exp(?:iry)?\s*date|best\s*before)\s*[:\.-]?\s*([0-9]{1,2}[\/\.-][0-9]{2,4}|[A-Za-z]{3,9}\s*[\/\.-]?\s*[0-9]{2,4}|\d+\s*months?)", re.IGNORECASE)
            ],
            "CONSUMER_CARE": [
                re.compile(r"(?:consumer\s*(?:care|cell|feedback|helpline)|contact|customercare)\s*[:\.-]?(.*)", re.IGNORECASE),
                re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|1800[-\s]?[0-9]{2,4}[-\s]?[0-9]{3,4})", re.IGNORECASE)
            ],
            "COUNTRY_OF_ORIGIN": [
                re.compile(r"(?:country\s*of\s*origin|made\s*in|imported\s*from)\s*[:\.-]?\s*([A-Za-z\s]+)", re.IGNORECASE)
            ],
            "FSSAI_NO": [
                re.compile(r"(?:fssai|lic(?:\.|\s*no)?)\s*[:\.-]?\s*([0-9]{14})", re.IGNORECASE)
            ],
            "MANUFACTURER_NAME_ADDRESS": [
                re.compile(r"(?:mfg(?:\.|ured)?\s*by|marketed\s*by|packed\s*by|imported\s*by)\s*[:\.-]?(.*)", re.IGNORECASE)
            ],
            "INGREDIENTS_LIST": [
                re.compile(r"(?:ingredients?|contains)\s*[:\.-]?(.*)", re.IGNORECASE)
            ],
            "ALLERGEN_WARNING": [
                re.compile(r"(?:allergen\s*(?:warning|advice|information)?|contains\s*(?:wheat|soy|milk|gluten|nuts|peanuts))\s*[:\.-]?(.*)", re.IGNORECASE)
            ]
        }

    def parse_food_safety_fields(self, full_text: str) -> Dict[str, Any]:
        """
        Parses food safety elements: Ingredients list, INS additives, Allergen declarations,
        and Nutritional panel values.
        """
        results = {
            "ingredients": [],
            "ins_additives": [],
            "allergens_detected": [],
            "nutritional_panel": {}
        }

        # 1. Parse Ingredients & INS Additives
        ing_match = re.search(r"(?:ingredients?|contains)\s*[:\.-]?(.*?)(?=(?:nutritional|nutrition|mfg|exp|fssai|storage|keep)|$)", full_text, re.IGNORECASE | re.DOTALL)
        if ing_match:
            ing_text = ing_match.group(1).strip()
            # Split ingredients by comma
            raw_items = [item.strip() for item in re.split(r'[,;]', ing_text) if item.strip()]
            results["ingredients"] = raw_items

            # Extract INS Additive numbers
            ins_matches = re.findall(r"\b(?:INS|E)\s*([0-9]{3,4}\s*(?:\([a-z0-9]+\))?)", full_text, re.IGNORECASE)
            results["ins_additives"] = [f"INS {ins.strip()}" for ins in ins_matches]

        # 2. Parse Allergen Warning
        allergen_keywords = ["gluten", "crustaceans", "milk", "dairy", "nuts", "peanuts", "soy", "soya", "wheat", "sulfites", "tree nuts"]
        for ak in allergen_keywords:
            if re.search(r"\b" + re.escape(ak) + r"\b", full_text, re.IGNORECASE):
                results["allergens_detected"].append(ak)

        # 3. Parse Nutritional Panel
        mandatory_nutrients = {
            "energy": r"energy\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*(?:kcal|kJ)?)",
            "protein": r"protein\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "carbohydrates": r"carbohydrates?\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "total_sugars": r"total\s*sugars?\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "added_sugars": r"added\s*sugars?\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "total_fat": r"total\s*fat\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "saturated_fat": r"saturated\s*fat\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "trans_fat": r"trans\s*fat\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*g?)",
            "sodium": r"sodium\s*[:\.-]?\s*(\d+(?:\.\d+)?\s*(?:mg|g)?)",
        }

        for nutrient, pattern in mandatory_nutrients.items():
            n_match = re.search(pattern, full_text, re.IGNORECASE)
            if n_match:
                results["nutritional_panel"][nutrient] = n_match.group(1).strip()

        return results

    def classify_tokens(self, ocr_tokens: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Maps OCR text items to statutory field classifications.
        Returns a dictionary keyed by field_name containing:
        - extracted_value
        - confidence
        - bbox
        - polygon
        - height_px
        """
        classified = {}
        unassigned_tokens = []

        # 1. Regex & Pattern Matching
        for token in ocr_tokens:
            text = token["text"]
            matched_field = None

            for field_name, regex_list in self.patterns.items():
                if field_name in classified:
                    continue  # already identified
                for pattern in regex_list:
                    match = pattern.search(text)
                    if match:
                        matched_field = field_name
                        classified[field_name] = {
                            "extracted_value": text,
                            "confidence": token["confidence"],
                            "bbox": token["bbox"],
                            "polygon": token["polygon"],
                            "height_px": token.get("height_px", 20.0),
                            "matched_substring": match.group(0)
                        }
                        break
                if matched_field:
                    break

            if not matched_field:
                unassigned_tokens.append(token)

        # 2. spaCy NER fallback for Manufacturer / Organization names
        if "MANUFACTURER_NAME_ADDRESS" not in classified and self.nlp and unassigned_tokens:
            for token in unassigned_tokens:
                doc = self.nlp(token["text"])
                for ent in doc.ents:
                    if ent.label_ in ["ORG", "GPE", "FAC"]:
                        classified["MANUFACTURER_NAME_ADDRESS"] = {
                            "extracted_value": token["text"],
                            "confidence": token["confidence"] * 0.85,
                            "bbox": token["bbox"],
                            "polygon": token["polygon"],
                            "height_px": token.get("height_px", 20.0),
                            "matched_substring": ent.text
                        }
                        break
                if "MANUFACTURER_NAME_ADDRESS" in classified:
                    break

        return classified

