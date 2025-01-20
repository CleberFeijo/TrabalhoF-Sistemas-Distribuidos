from celery import Celery
from celery.schedules import crontab
from core.settings import env_settings

# Configuração do Celery
celery_app = Celery(
    "tasks",
    broker=env_settings.CELERY_BROKER_API_URL,
    backend=env_settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.timezone = "UTC"

# Tarefa para testes
@celery_app.task
def print_hello():
    print("Hello, Celery Beat!")

# Configurar tarefas periódicas no Celery Beat
celery_app.conf.beat_schedule = {
    "print-hello-every-30-seconds": {
        "task": "tasks.print_hello",
        "schedule": 30.0,  # Executa a cada 30 segundos
    },
    # Exemplo com crontab
    "print-hello-every-day": {
        "task": "tasks.print_hello",
        "schedule": crontab(hour=0, minute=0),  # Executa à meia-noite
    },
}
