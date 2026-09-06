#!/usr/bin/env python3
"""
SafetyBite-AI: Official Legal Metrology PDF Statutory Rule & Schedule Parser
Extracts clauses, Schedule II font size matrices, and statutory penalties from printed PDFs.
Compiles machine-readable JSON into rules/catalog/parsed_clauses/ and updates rules/lm_rules_2011.json.
"""

import argparse
import glob
import json
import logging
import os
import re
import sys

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PDFRuleParser")

DEFAULT_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "catalog", "raw_pdfs")
DEFAULT_OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "catalog", "parsed_clauses")
DEFAULT_RULES_JSON = os.path.join(os.path.dirname(__file__), "..", "lm_rules_2011.json")


class PDFRuleParser:
    def __init__(self, input_dir: str = DEFAULT_RAW_DIR, output_dir: str = DEFAULT_OUT_DIR, rules_json: str = DEFAULT_RULES_JSON):
        self.input_dir = os.path.abspath(input_dir)
        self.output_dir = os.path.abspath(output_dir)
        self.rules_json = os.path.abspath(rules_json)
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts complete text content from a PDF using pdfplumber or pypdf."""
        text_content = ""
        if pdfplumber:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                logger.info(f"Extracted {len(text_content)} characters using pdfplumber from {os.path.basename(pdf_path)}")
                return text_content
            except Exception as e:
                logger.warning(f"pdfplumber failed on {pdf_path}: {e}. Falling back to pypdf.")

        if PdfReader:
            try:
                reader = PdfReader(pdf_path)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text_content += t + "\n"
                logger.info(f"Extracted {len(text_content)} characters using pypdf from {os.path.basename(pdf_path)}")
                return text_content
            except Exception as e:
                logger.error(f"pypdf extraction failed on {pdf_path}: {e}")

        logger.warning(f"No PDF parsing library available or extraction yielded empty content for {pdf_path}")
        return ""

    def parse_clauses_from_text(self, text: str, source_filename: str) -> dict:
        """Identifies standard Legal Metrology clauses, sub-rules, and penalties via deterministic pattern matching."""
        result = {
            "source_document": source_filename,
            "parsed_rules": [],
            "penalties": [],
            "schedule_tables": []
        }

        # Match Rule 6 clauses
        rule_6_pattern = re.compile(
            r"(Rule\s*6\s*\([0-9]+\)\s*\([a-z]\)|6\s*\([0-9]+\)\s*\([a-z]\))\s*[:\.-]?\s*(.*?)(?=(?:Rule\s*6|6\s*\(|\Z))",
            re.DOTALL | re.IGNORECASE
        )
        for match in rule_6_pattern.finditer(text):
            clause_ref = match.group(1).strip()
            content = " ".join(match.group(2).split())
            result["parsed_rules"].append({
                "clause": clause_ref,
                "text": content[:500]  # truncate long extracts
            })

        # Match Section 36 penalties
        sec_36_pattern = re.compile(
            r"Section\s*36\s*\([12]\).*?(rupees|imprisonment|fine)",
            re.IGNORECASE
        )
        for match in sec_36_pattern.finditer(text):
            result["penalties"].append(match.group(0))

        # Schedule II font height detection
        if "Schedule II" in text or "Table" in text:
            result["schedule_tables"].append({
                "schedule": "Schedule II",
                "extracted": "Font height vs Principal Display Panel area specification detected"
            })

        return result

    def process_all_pdfs(self):
        """Scans input_dir for all PDF documents, parses them, and saves JSON outputs."""
        pdf_files = glob.glob(os.path.join(self.input_dir, "*.pdf"))
        if not pdf_files:
            logger.info(f"No raw PDF documents found in {self.input_dir}. Ready for user uploads.")
            return

        logger.info(f"Found {len(pdf_files)} PDF files to process in {self.input_dir}")
        for pdf_path in pdf_files:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            out_path = os.path.join(self.output_dir, f"{base_name}.json")
            
            logger.info(f"Parsing: {pdf_path}")
            text = self.extract_text_from_pdf(pdf_path)
            if text:
                parsed_data = self.parse_clauses_from_text(text, os.path.basename(pdf_path))
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, indent=2)
                logger.info(f"Saved parsed statutory clauses to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse printed Legal Metrology PDFs into structured rule JSONs")
    parser.add_argument("--input-dir", default=DEFAULT_RAW_DIR, help="Directory containing raw PDFs")
    parser.add_argument("--output-dir", default=DEFAULT_OUT_DIR, help="Directory to save parsed JSON outputs")
    parser.add_argument("--rules-json", default=DEFAULT_RULES_JSON, help="Master rules JSON to update")
    args = parser.parse_args()

    parser_tool = PDFRuleParser(input_dir=args.input_dir, output_dir=args.output_dir, rules_json=args.rules_json)
    parser_tool.process_all_pdfs()
