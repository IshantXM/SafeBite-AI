# Legal Metrology Statutory Rules & Acts Catalog

This directory serves as the official document repository and ingestion catalog for statutory enactments under the **Ministry of Consumer Affairs, Food and Public Distribution (DOCA), Government of India**.

---

## Directory Structure

```
rules/catalog/
├── catalog_manifest.json     # Master index registry of all Acts, Rules & Gazette Amendments
├── raw_pdfs/                 # Drop printed / official Gazette PDFs here
│   ├── legal_metrology_act_2009.pdf
│   ├── lm_packaged_commodities_rules_2011.pdf
│   ├── lm_amendment_rules_2017.pdf
│   └── lm_amendment_rules_2021.pdf
└── parsed_clauses/           # Automated structured JSON outputs extracted by pdf_rule_parser.py
    ├── lm_act_2009.json
    └── packaged_commodities_rules_2011.json
```

---

## How to Ingest New Statutory PDFs

1. **Drop your PDF documents** into the `raw_pdfs/` folder.
2. **Update the catalog manifest** (`catalog_manifest.json`) with the document title, gazette notification number, and enforcement date.
3. **Run the PDF parser**:
   ```bash
   python rules/scrapers/pdf_rule_parser.py --input-dir rules/catalog/raw_pdfs --output-dir rules/catalog/parsed_clauses
   ```
4. The parser will extract:
   - Clause hierarchies (Rule 6(1)(a) through Rule 6(1)(f), Rule 7, etc.)
   - Minimum font height tables according to package surface area ($A \le 50\text{ cm}^2$, etc.)
   - Statutory penalties under Section 36 of the Legal Metrology Act, 2009
   - Updates `rules/lm_rules_2011.json` automatically, which is read live by the AI rule validation engine.

---

## Automated Web Scraping from DOCA Portal

To automatically discover, scrape, and download the latest gazette notifications and official circulars from the official government portal:
```bash
python rules/scrapers/doca_web_scraper.py --output-dir rules/catalog/raw_pdfs
```
This utility connects to `https://consumeraffairs.nic.in/acts-and-rules/legal-metrology`, traverses statutory publications, detects new or amended PDFs, computes SHA-256 integrity hashes, updates `catalog_manifest.json`, and triggers the PDF parser.
