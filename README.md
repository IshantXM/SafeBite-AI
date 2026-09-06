# LMS-Sentinel (Legal Metrology Sentinel)

**AI-Powered Legal Metrology Compliance Verification and Enforcement System**  
*Department of Consumer Affairs (DOCA), Ministry of Consumer Affairs, Food and Public Distribution, Government of India*

---

## 1. System Overview

**LMS-Sentinel** is an enterprise-grade, end-to-end legal metrology compliance enforcement monorepo. It automates the detection, measurement, and judicial notice generation for packaged commodities under the statutory mandate of:
- **The Legal Metrology Act, 2009** (Act No. 1 of 2010, Sections 18 & 36)
- **The Legal Metrology (Packaged Commodities) Rules, 2011** (G.S.R. 202(E) and 2017/2021 Amendments)
  - **Rule 6(1)(a)**: Name and complete address of manufacturer/packer/importer.
  - **Rule 6(1)(b)**: Generic commodity name & Net quantity in standard SI units (`g`, `kg`, `ml`, `l`, `m`, `N`, `U`), strictly prohibiting qualifiers ("approx", "when packed", "jumbo").
  - **Rule 6(1)(c)**: Maximum Retail Price (MRP) mandatory phrase *"inclusive of all taxes"* or *"incl. of all taxes"*, currency symbol (`₹` / `Rs.`), and Unit Sale Price (USP).
  - **Rule 6(1)(d)**: Month & year of manufacture / pre-packing / import.
  - **Rule 6(1)(e)**: Consumer care grievance details (helpline, email, address).
  - **Rule 6(1)(f)**: Country of origin on imported packaged commodities.
  - **Rule 7 / Schedule II**: Minimum font/numeral height scale mapped to Principal Display Panel (PDP) surface area ($A \le 50\text{ cm}^2 \to 1.0\text{ mm}$, $50 < A \le 200 \to 2.0\text{ mm}$, $200 < A \le 1000 \to 4.0\text{ mm}$, $A > 1000 \to 6.0\text{ mm}$).
  - **Tamper Detection**: Overlapping adhesive stickers concealing underlying printed declarations.

---

## 2. Monorepo Architecture

```
lms-sentinel/
├── apps/
│   ├── mobile/                  # Flutter (Dart 3.x) Offline-first Field App (Riverpod, SQLite, CameraX)
│   └── web-dashboard/           # React 18 + TypeScript + Vite + Tailwind CSS Admin Portal
├── services/
│   ├── api-gateway/             # NGINX reverse proxy, rate limiter & SSL/CORS router
│   ├── core-api/                # FastAPI (Async) + SQLAlchemy 2.0 + PostgreSQL 16/PostGIS + Alembic
│   ├── ai-inference/            # Celery Worker + OpenCV (CLAHE/Hough) + YOLOv8 + PaddleOCR v4 + spaCy + Calibrator
│   └── report-generator/        # WeasyPrint PDF notice generator with X.509 PKI digital signing
├── rules/                       # Version-controlled statutory rule engine
│   ├── catalog/                 # File Catalog for user-provided Legal Metrology Act & Rules PDFs/Gazettes
│   │   ├── catalog_manifest.json# Manifest registry of statutory enactments, amendments & gazette notifications
│   │   ├── raw_pdfs/            # Directory to drop official Legal Metrology Act & Rules PDFs
│   │   └── parsed_clauses/      # Structured clause-by-clause extracted JSON databases
│   ├── scrapers/                # Web & PDF scraping pipeline (DOCA portal scraper + PDF parser)
│   │   ├── doca_web_scraper.py  # DOCA portal web crawler & downloader
│   │   └── pdf_rule_parser.py   # PDF layout and schedule table parser
│   └── lm_rules_2011.json       # Production rule schema loaded by the validation engine
├── deploy/                      # Docker Compose & Kubernetes production manifests
│   ├── docker-compose.yml       # Production Compose file for 10 microservices
│   └── k8s/                     # Deployments, Services, ConfigMaps, Secrets, Ingress
├── Makefile                     # Root automation (init, migrate, test, dev, build)
└── .env.example                 # Production environment variable specifications
```

---

## 3. Statutory File Catalog & Web/PDF Scraper

### Ingesting Printed Rules & Act PDFs
You can provide official printed PDFs of the Legal Metrology Act, 2009, Packaged Commodities Rules, 2011, and any Gazette Notifications:
1. Drop your printed PDF files directly into `rules/catalog/raw_pdfs/`.
2. Run the PDF extraction pipeline:
   ```bash
   python rules/scrapers/pdf_rule_parser.py --input-dir rules/catalog/raw_pdfs --output-dir rules/catalog/parsed_clauses
   ```
   This extracts statutory clauses, Schedule II font size matrices, and Section 36 penalties into structured JSON, updating `rules/lm_rules_2011.json`.

### Automated Web Scraping from DOCA Portal
To crawl and download the latest gazettes, acts, and rules directly from the Ministry of Consumer Affairs portal:
```bash
python rules/scrapers/doca_web_scraper.py --output-dir rules/catalog/raw_pdfs
```
The scraper computes SHA-256 integrity hashes for each downloaded PDF and registers them in `rules/catalog/catalog_manifest.json`.

---

## 4. Key Subsystems

### A. Core API (`services/core-api/`)
- Built with **FastAPI Async**, **SQLAlchemy 2.0**, and **PostGIS (GeoAlchemy2)**.
- Full **Alembic** migration suite with spatial indexing on seizure coordinates.
- Keycloak JWT RBAC supporting `Inspector`, `Supervisor`, `Admin`, and `Brand` roles.
- MinIO S3 client for package imagery and immutable append-only `audit_logs`.

### B. AI Vision & Calibration Pipeline (`services/ai-inference/`)
- **CLAHE & Hough Deskewing (`preprocessor.py`)**: Normalizes gloss/glare and straightens packaging panels.
- **YOLOv8 Region Detection (`region_detector.py`)**: Locates Principal Display Panel (PDP), barcode, and suspect price sticker overlays.
- **PaddleOCR v4 (`ocr_engine.py`)**: High-accuracy multi-angle text extraction across Latin and Devanagari scripts.
- **Metric Spatial Calibrator (`font_calibrator.py`)**: Uses GS1 EAN-13 nominal width ($37.29\text{ mm}$) to compute physical scale ($\text{mm/px}$) and calculates font heights directly in millimeters ($\text{mm}$).
- **WCAG 2.1 Contrast Checker (`contrast_checker.py`)**: Assesses relative luminance of text against substrate.
- **Statutory Rule Validator (`validator.py`)**: Deterministic evaluation against Rule 6(1)(a)-(f) and Schedule II font height thresholds.

### C. PKI Statutory Notice Generator (`services/report-generator/`)
- Renders official Government of India show cause notices using **WeasyPrint** and Jinja2 templates.
- Signs the PDF cryptographically using **X.509 PKI certificates** and RSA-2048 keys.
- Embeds SHA-256 image hashes, seizure GPS coordinates, inspector UUIDs, and itemized Section 36 penalty breakdowns.

### D. Supervisory Web Dashboard (`apps/web-dashboard/`)
- **React 18 + TypeScript + Vite + Tailwind CSS**.
- **Command Center**: GIS GeoJSON cluster heatmap of violation density, live KPI metrics, repeat offender watchlist.
- **Case Management Kanban**: Status transitions (`Flagged` $\to$ `Review` $\to$ `Notice Issued` $\to$ `Resolved`).
- **Visual Evidence Inspector**: Canvas/SVG overlay viewer with measured font heights (mm), contrast ratios, and human-in-the-loop override drawer.
- **Brand Self-Check Portal**: Pre-market compliance upload portal for FMCG manufacturers.
- **Rule Admin Console**: Visual schema editor to adjust penalty scales and font height matrices.

### E. Field Mobile Application (`apps/mobile/`)
- **Flutter 3.x + Riverpod + SQLite**.
- **Edge Quality Gate**: Real-time on-device Laplacian blur checks ($\text{variance} \ge 100$) and luminance glare detection before capture.
- **Chain-of-Custody**: Computes SHA-256 cryptographic image hash bound to hardware GPS coordinates and UTC timestamps at capture.
- **Offline Ledger**: SQLite storage with automatic background synchronization via `WorkManager` when network connectivity is restored.

---

## 5. Quick Start Guide

### Prerequisites
- Docker Engine & Docker Compose
- Python 3.10+ (for local scripts/tests)
- Node.js 20+ (for web dashboard development)
- Flutter 3.x (for mobile application)

### 1. Initialize Configuration
```bash
make init
# Copies .env.example to .env and creates required catalog directories
```

### 2. Build & Launch Monorepo Services
```bash
make build
make up
```

### 3. Run Database Migrations & Seed Rules
```bash
make migrate
make seed
```

### 4. Access Running Services
- **Web Dashboard**: [http://localhost](http://localhost) (or [http://localhost:5173](http://localhost:5173) in dev)
- **Core API Docs (Swagger)**: [http://localhost/docs](http://localhost/docs)
- **MinIO Object Storage Console**: [http://localhost:9001](http://localhost:9001)
- **Keycloak IAM**: [http://localhost:8080](http://localhost:8080)

---

## 6. Running Automated Tests

```bash
# Test Core API
cd services/core-api && pytest -v

# Test AI Vision Pipeline & Statutory Rule Engine
cd services/ai-inference && pytest -v
```

---

## 7. License & Compliance
This software is developed in accordance with the statutory requirements of the **Legal Metrology Act, 2009** and the **Legal Metrology (Packaged Commodities) Rules, 2011**, under the Ministry of Consumer Affairs, Food and Public Distribution, Government of India.
