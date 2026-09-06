import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://:sentinel_redis_pass_2026@redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://:sentinel_redis_pass_2026@redis:6379/1"
    DATABASE_SYNC_URL: str = "postgresql://sentinel_admin:sentinel_secure_password_2026@postgres-postgis:5432/lms_sentinel"
    
    # Model configs
    YOLO_MODEL_PATH: str = "/app/models/yolov8_lms_package_v1.pt"
    PADDLE_OCR_LANG: str = "en"
    SPACY_MODEL: str = "en_core_web_sm"

    # Calibration standard (Nominal EAN-13 physical barcode dimensions in mm)
    EAN13_NOMINAL_WIDTH_MM: float = 37.29

    # OpenCV CLAHE defaults
    CLAHE_CLIP_LIMIT: float = 2.5
    CLAHE_GRID_SIZE: int = 8

    # Rules schema path
    RULES_JSON_PATH: str = "/app/rules/lm_rules_2011.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


worker_settings = WorkerSettings()
