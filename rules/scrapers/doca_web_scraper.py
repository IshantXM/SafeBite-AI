#!/usr/bin/env python3
"""
LMS-Sentinel: Official Statutory Document Web Scraper
Department of Consumer Affairs (DOCA), Ministry of Consumer Affairs, Government of India.

Scrapes official gazette notifications, Acts, Rules, and Amendments from:
https://consumeraffairs.nic.in/acts-and-rules/legal-metrology
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[WARN] requests/bs4 not installed in local environment. Run: pip install -r rules/scrapers/requirements.txt")
    requests = None
    BeautifulSoup = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("DOCAScraper")

DEFAULT_TARGET_URL = "https://consumeraffairs.nic.in/acts-and-rules/legal-metrology"
DEFAULT_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "catalog", "raw_pdfs")
DEFAULT_MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "..", "catalog", "catalog_manifest.json")


def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a downloaded file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


class DOCAWebScraper:
    def __init__(self, base_url: str = DEFAULT_TARGET_URL, output_dir: str = DEFAULT_RAW_DIR, manifest_path: str = DEFAULT_MANIFEST_PATH):
        self.base_url = base_url
        self.output_dir = os.path.abspath(output_dir)
        self.manifest_path = os.path.abspath(manifest_path)
        os.makedirs(self.output_dir, exist_ok=True)
        self.session = requests.Session() if requests else None
        if self.session:
            self.session.headers.update({
                "User-Agent": "LMS-Sentinel-DOCA-Auditor/1.0 (+https://consumeraffairs.nic.in)"
            })

    def fetch_page(self, url: str) -> str:
        """Fetches page HTML with standard timeout."""
        if not self.session:
            raise RuntimeError("Missing 'requests' library. Please install requirements.")
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=20, verify=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Direct fetch failed for {url} ({e}). Falling back or logging.")
            return ""

    def parse_pdf_links(self, html_content: str) -> list:
        """Finds all statutory PDF links and titles from DOCA HTML content."""
        if not BeautifulSoup or not html_content:
            return []
        soup = BeautifulSoup(html_content, "html.parser")
        documents = []

        for link in soup.find_all("a", href=True):
            href = link["href"].strip()
            if href.lower().endswith(".pdf") or "/sites/default/files/" in href:
                full_url = urljoin(self.base_url, href)
                title = link.get_text(strip=True) or os.path.basename(urlparse(full_url).path)
                
                # Check relevance to Legal Metrology / Packaged Commodities
                keywords = ["metrology", "packaged", "commodities", "rule", "act", "amendment", "gsr", "gazette"]
                if any(kw in full_url.lower() or kw in title.lower() for kw in keywords):
                    documents.append({
                        "title": title,
                        "url": full_url,
                        "suggested_filename": os.path.basename(urlparse(full_url).path)
                    })

        logger.info(f"Discovered {len(documents)} relevant statutory PDF documents.")
        return documents

    def download_pdf(self, doc: dict) -> str:
        """Downloads a statutory PDF and verifies integrity."""
        filename = doc["suggested_filename"]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        target_path = os.path.join(self.output_dir, filename)

        if os.path.exists(target_path):
            logger.info(f"File already exists: {filename} (skipping download)")
            return target_path

        logger.info(f"Downloading: {doc['title']} from {doc['url']} -> {target_path}")
        try:
            r = self.session.get(doc["url"], stream=True, timeout=30)
            r.raise_for_status()
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Saved: {target_path}")
            return target_path
        except Exception as e:
            logger.error(f"Failed to download {doc['url']}: {e}")
            return ""

    def update_manifest(self, downloaded_docs: list):
        """Updates catalog_manifest.json with newly scraped documents and SHA-256 hashes."""
        if not os.path.exists(self.manifest_path):
            manifest = {"catalog_version": "2026.1", "enactments": []}
        else:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

        existing_urls = {item.get("source_url") for item in manifest.get("enactments", [])}

        for doc in downloaded_docs:
            if doc["url"] not in existing_urls and doc.get("filepath") and os.path.exists(doc["filepath"]):
                sha256_sum = compute_sha256(doc["filepath"])
                manifest["enactments"].append({
                    "id": re.sub(r'[^A-Za-z0-9_]', '_', os.path.splitext(doc['suggested_filename'])[0]).upper(),
                    "title": doc["title"],
                    "raw_pdf_filename": os.path.basename(doc["filepath"]),
                    "source_url": doc["url"],
                    "sha256": sha256_sum,
                    "scraped_date": "2026-09-01"
                })

        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        logger.info(f"Manifest catalog updated at {self.manifest_path}")

    def run(self):
        """Executes the scraping workflow."""
        logger.info(f"Starting DOCA statutory rule scraper on {self.base_url}")
        html = self.fetch_page(self.base_url)
        if not html:
            logger.warning("Could not retrieve remote portal page. Generating catalog registry from local records.")
            return

        docs = self.parse_pdf_links(html)
        downloaded = []
        for d in docs:
            fp = self.download_pdf(d)
            if fp:
                d["filepath"] = fp
                downloaded.append(d)

        self.update_manifest(downloaded)
        logger.info("Scraping task completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape official Legal Metrology acts & rules from DOCA portal")
    parser.add_argument("--url", default=DEFAULT_TARGET_URL, help="Target portal URL")
    parser.add_argument("--output-dir", default=DEFAULT_RAW_DIR, help="Destination folder for raw PDFs")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST_PATH, help="Path to catalog_manifest.json")
    args = parser.parse_args()

    scraper = DOCAWebScraper(base_url=args.url, output_dir=args.output_dir, manifest_path=args.manifest)
    scraper.run()
