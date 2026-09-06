import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "LMS-Sentinel Core API"
    SECRET_KEY: str = "sentinel_prod_sec_key_change_in_production_89f1a23c4d5e"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://sentinel.consumeraffairs.gov.in"
    ]

    # Database URLs
    DATABASE_URL: str = "postgresql+asyncpg://sentinel_admin:sentinel_secure_password_2026@postgres-postgis:5432/lms_sentinel"
    DATABASE_SYNC_URL: str = "postgresql://sentinel_admin:sentinel_secure_password_2026@postgres-postgis:5432/lms_sentinel"

    # Redis / Celery
    CELERY_BROKER_URL: str = "redis://:sentinel_redis_pass_2026@redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:sentinel_redis_pass_2026@redis:6379/1"

    # MinIO / S3
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "sentinel_minio_admin"
    MINIO_ROOT_PASSWORD: str = "sentinel_minio_secret_key_2026"
    MINIO_BUCKET_INSPECTIONS: str = "sentinel-inspections"
    MINIO_BUCKET_REPORTS: str = "sentinel-reports"
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_URL: str = "http://localhost:9000"

    # Elasticsearch
    ELASTICSEARCH_HOST: str = "http://elasticsearch:9200"
    ELASTICSEARCH_USER: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = "sentinel_elastic_pass_2026"

    # Report Generator
    REPORT_GENERATOR_URL: str = "http://report-generator:8002"

    # Keycloak
    KEYCLOAK_SERVER_URL: str = "http://keycloak:8080"
    KEYCLOAK_REALM: str = "lms-sentinel"
    KEYCLOAK_CLIENT_ID: str = "sentinel-api"
    KEYCLOAK_CLIENT_SECRET: str = "sentinel_keycloak_secret_2026"
    KEYCLOAK_PUBLIC_KEY: str = ""

    # Google OAuth2 Social Sign-In
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # LLM API Keys (Gemini / OpenAI for advanced NER / Statutory reasoning fallback)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Rules Schema Path
    RULES_JSON_PATH: str = "/app/rules/lm_rules_2011.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
