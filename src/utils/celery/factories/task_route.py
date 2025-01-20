__all__ = 'TaskRoute',


class TaskRoute(str):
    """
    Subclasse de string, responsável por padronizar o nome das tarefas e
    armazenar os dados referentes ao vínculos de fila e aplicação do celery.

    - O método `_create_task_name` é responsável por criar a nomenclatura
      completa da tarefa durante a instanciação. Por padrão, utiliza o formato
      "<nome-da-fila>.<nome-da-tarefa>", mas pode ser sobrescrito na subclasse.
    """
    def __new__(cls, queue: str, task: str) -> 'TaskRoute':
        instance = super().__new__(cls, cls._create_task_name(queue, task))
        instance._queue_name = queue
        instance._task_name = task
        return instance

    @property
    def queue_name(self) -> str:
        """Retorna o nome da fila."""
        return self._queue_name

    @property
    def task_name(self) -> str:
        """
        Retorna o nome original da tarefa, antes a composição criada pelo
        método `_create_task_name`.
        """
        return self._task_name

    @property
    def route(self) -> dict:
        """
        Retorna o dict usado para definir a correlação entre tarefa e fila.

        - Usado pela config. `task_routes` do Celery.
        """
        return {self: {'queue': self.queue_name}}

    @staticmethod
    def _create_task_name(queue: str, task: str):
        return f'{queue}.{task}'
