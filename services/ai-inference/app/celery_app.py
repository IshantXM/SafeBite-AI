from celery import Celery
from app.config import worker_settings

celery_app = Celery(
    "lms_ai_inference",
    broker=worker_settings.CELERY_BROKER_URL,
    backend=worker_settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_routes={
        "app.tasks.*": {"queue": "lms_inference_queue"}
    }
)
