.PHONY: help init build up down logs restart migrate test seed clean scrape-rules parse-rules

help:
	@echo "SafetyBite-AI (Legal Metrology Sentinel) - Command Automation"
	@echo "------------------------------------------------------------"
	@echo "make init          - Initialize development environment and copies .env"
	@echo "make build         - Build all Docker service images"
	@echo "make up            - Launch all services with Docker Compose"
	@echo "make down          - Stop all running containers"
	@echo "make restart       - Restart all containers"
	@echo "make logs          - Tail logs from all containers"
	@echo "make migrate       - Run Alembic database migrations"
	@echo "make test          - Execute automated test suites"
	@echo "make seed          - Seed initial statutory rules & admin users"
	@echo "make scrape-rules  - Scrape DOCA portal for latest rules & amendments"
	@echo "make parse-rules   - Parse raw statutory PDFs in rules/catalog/raw_pdfs"
	@echo "make clean         - Remove build artifacts and temporary files"

init:
	cp -n .env.example .env || true
	mkdir -p rules/catalog/raw_pdfs rules/catalog/parsed_clauses
	mkdir -p services/report-generator/certs
	@echo "Environment initialized. Customize .env if needed."

build:
	docker compose -f deploy/docker-compose.yml build

up:
	docker compose -f deploy/docker-compose.yml up -d

down:
	docker compose -f deploy/docker-compose.yml down

restart: down up

logs:
	docker compose -f deploy/docker-compose.yml logs -f

migrate:
	docker compose -f deploy/docker-compose.yml exec core-api alembic upgrade head

test:
	docker compose -f deploy/docker-compose.yml exec core-api pytest -v
	docker compose -f deploy/docker-compose.yml exec ai-inference pytest -v

seed:
	docker compose -f deploy/docker-compose.yml exec core-api python -m app.scripts.seed_rules

scrape-rules:
	python rules/scrapers/doca_web_scraper.py --output-dir rules/catalog/raw_pdfs

parse-rules:
	python rules/scrapers/pdf_rule_parser.py --input-dir rules/catalog/raw_pdfs --output-dir rules/catalog/parsed_clauses

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
