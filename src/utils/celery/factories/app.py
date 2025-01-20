from celery import Celery, Task

from common.classes import UNDEFINED
from common.typealiases import ModuleT, Sequence, Union

from ..functions import register_class_based_tasks

__all__ = 'CeleryFactory',


class CeleryFactory:

    def __new__(
            cls,
            name: str = 'app',
            config: Union[str, dict, object, None] = UNDEFINED,
            tasks: Union[ModuleT, Sequence, Task, None] = None,
    ) -> Celery:
        """
        Classe responsável por criar uma instância do Celery, aplicando suas
        configurações e, caso necessário, registrando as tarefas do Celery
        baseadas em classe.

        :param name: Nome da aplicação Celery.
        :param config: Configuração opcional do Celery.
        :param tasks: Módulo, Tarefa ou Sequência de tarefas do celery criadas
            a partir de classes.
        """
        app = Celery(name)
        if config:
            app.config_from_object(config)
        if tasks:
            register_class_based_tasks(app=app, class_based_tasks=tasks)
        return app
