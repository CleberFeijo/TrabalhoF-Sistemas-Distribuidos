"""Aplicação Celery para tarefas em segundo plano (ex.: o crawler de pontos históricos).

Executar o worker:
    celery -A app.worker.celery_app worker --loglevel=info
"""
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("hist", broker=settings.CELERY_BROKER_URL, include=["app.worker.tasks"])
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_ignore_result=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    timezone="America/Sao_Paulo",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
