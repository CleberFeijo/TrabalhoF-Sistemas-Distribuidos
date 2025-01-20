from celery import Celery, Task

from common.classes import ModuleIterator
from common.typealiases import Any, ModuleT, Sequence, Type

__all__ = 'register_class_based_tasks',


def register_class_based_tasks(app: Celery, class_based_tasks: Any):
    """
    Recebe uma classe, módulo ou sequência contendo as classes que são
    implementações de tarefas do Celery, registrando-as na aplicação informada.

    - Objetiva reduzir a necessidade de cadastrar individualmente cada tarefa
      e permitir subclasses de "utils.celery.classes.Task" ao invés da Task
      de base do Celery.
    - Só cadastra tarefas que possuem o campo "name" definido.

    :param app: Instância do celery que criará vínculo com a tarefa.
    :param class_based_tasks: Classe, módulo ou sequência com as classes.
    """

    for cbt in _it_class_based_tasks(class_based_tasks):
        if not cbt.name:
            continue
        app.register_task(cbt())


def _it_class_based_tasks(cbt: Any) -> Type[Task]:
    if isinstance(cbt, ModuleT):
        yield from ModuleIterator(cbt).it_classes(Task)
    elif isinstance(cbt, Sequence):
        for _cbt in cbt:
            yield from _it_class_based_tasks(_cbt)
    elif isinstance(cbt, type) and issubclass(cbt, Task):
        yield cbt
