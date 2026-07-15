"""Celery worker application for asynchronous tasks."""

from al_syaka_common.config import settings
from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    "al_syaka_quant",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Import tasks to register them
import src.tasks.market_data  # noqa: F401
import src.tasks.processing  # noqa: F401

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # H4: every 4 hours (recommended: top of every 4th hour)
        "fetch-ohlc-h4": {
            "task": "fetch_ohlc_h4",
            "schedule": 14400.0,  # 4 hours
            "options": {"queue": "data_collection"},
        },
        # D1: once daily at 00:30 UTC (after market close)
        "fetch-ohlc-d1": {
            "task": "fetch_ohlc_d1",
            "schedule": crontab(hour=0, minute=30),
            "options": {"queue": "data_collection"},
        },
    },
)
