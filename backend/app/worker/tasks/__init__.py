"""Tarefas Celery. As tarefas do crawler serão registradas aqui."""
from app.worker.celery_app import celery_app


@celery_app.task(name="hist.ping")
def ping() -> str:
    """Tarefa trivial para verificar se o worker está consumindo a fila."""
    return "pong"
