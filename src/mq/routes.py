from utils.celery import QueueRoute, QueueArguments, TaskRoute

__all__ = 'CeleryQueueConf', 'CeleryTaskConf',


class CeleryQueueConf:
    """Contém o nome das filas da aplicação celery principal."""
    BACKGROUND = QueueRoute(
        queue='background',
        queue_arguments=QueueArguments(max_priority=9),
    )

    @classmethod
    def default(cls):
        return cls.BACKGROUND

    @classmethod
    def task_queues(cls):
        for k, v in cls.__dict__.items():
            if not k.startswith('_') and isinstance(v, QueueRoute):
                yield v.queue


class CeleryTaskConf:
    """Contém o nome das tarefas da aplicação celery principal."""
    EXEMPLO = TaskRoute(
        queue=CeleryQueueConf.BACKGROUND,
        task='async_exemplo',
    )

    @classmethod
    def task_routes(cls):
        routes = {}
        for k, v in cls.__dict__.items():
            if not k.startswith('_') and isinstance(v, TaskRoute):
                routes.update(v.route)
        return routes
