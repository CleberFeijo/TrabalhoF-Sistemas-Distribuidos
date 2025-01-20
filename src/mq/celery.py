from celery.schedules import crontab

from core.settings import env_settings
from utils.celery import CeleryFactory, CeleryConfig, BeatSchedule

from . import tasks
from .routes import CeleryQueueConf, CeleryTaskConf

__all__ = 'app',


app = CeleryFactory(
    name='app',
    tasks=tasks,
    config=CeleryConfig(
        beat_schedule=BeatSchedule.create_schedules([
            BeatSchedule(
                task=CeleryTaskConf.EXEMPLO,
                schedule=crontab(minute='0,30'),
            ),
        ]),
        broker_url=env_settings.CELERY_BROKER_API_URL,
        # imports=['mq.tasks'],  # Não funciona com "Class-Based Tasks".
        result_backend=env_settings.CELERY_RESULT_BACKEND,
        result_expires=1,
        task_acks_late=True,
        task_default_queue=CeleryQueueConf.default(),
        task_ignore_result=True,
        task_queues=list(CeleryQueueConf.task_queues()),
        task_serializer='json',
        task_routes=CeleryTaskConf.task_routes(),
        timezone='AMERICA/SAO_PAULO',
        worker_cancel_long_running_tasks_on_connection_loss=True,
        worker_hijack_root_logger=False,
        worker_max_tasks_per_child=1000,
        worker_prefetch_multiplier=10,
    ),
)
