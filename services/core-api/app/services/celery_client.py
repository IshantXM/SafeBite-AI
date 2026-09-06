import logging
import uuid
from celery import Celery
from app.config import settings

logger = logging.getLogger("CeleryClient")

celery_app = Celery(
    "lms_sentinel_client",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
)


def dispatch_inspection_pipeline(inspection_id: uuid.UUID) -> str:
    """Dispatches the AI vision pipeline task asynchronously to the Celery worker queue."""
    try:
        task = celery_app.send_task(
            "app.tasks.process_inspection_task",
            args=[str(inspection_id)],
            queue="lms_inference_queue"
        )
        logger.info(f"Dispatched Celery task {task.id} for inspection {inspection_id}")
        return task.id
    except Exception as e:
        logger.error(f"Failed to dispatch Celery task for inspection {inspection_id}: {e}")
        # In isolated environments without Redis, generate a tracking ID
        return f"local-job-{uuid.uuid4()}"
