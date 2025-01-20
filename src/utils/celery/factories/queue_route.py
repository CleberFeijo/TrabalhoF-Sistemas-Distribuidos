from kombu import Exchange, Queue
from typing import Any, Union

from common.classes import UNDEFINED

from ..models import QueueArguments

__all__ = 'QueueRoute',


class QueueRoute(str):
    """
    Subclasse de string, responsável por padronizar o nome da fila e
    armazenar os dados referentes ao vínculo da aplicação do celery e os dados
    de criação da fila.

    - O método `_create_queue_name` é responsável por criar a nomenclatura
      completa da fila durante a instanciação. Por padrão, utiliza o formato
      "<nome-do-projeto>.<nome-da-fila>", mas pode ser sobrescrito na subclasse.
    """
    def __new__(
            cls,
            queue: str,
            *,
            exchange: Union[str, Exchange, None] = UNDEFINED,
            routing_key: str = UNDEFINED,
            # channel: Any = UNDEFINED,
            # bindings: Any = UNDEFINED,
            # on_declared: Any = UNDEFINED,
            queue_arguments: Union[dict, object, QueueArguments, None] = UNDEFINED,
    ) -> 'QueueRoute':
        instance = super().__new__(cls, cls._create_queue_name(queue))
        instance._queue_name = queue
        instance._queue_init_kwargs = {
            'routing_key': routing_key,
            'exchange': exchange,
            # channel: Any = UNDEFINED,
            # bindings: Any = UNDEFINED,
            # on_declared: Any = UNDEFINED,
            'queue_arguments': queue_arguments,
        }
        return instance

    @property
    def queue_name(self) -> str:
        """
        Retorna o nome original da fila, antes a composição criada pelo
        método `_create_queue_name`.
        """
        return self._queue_name

    @property
    def queue(self) -> Queue:
        """
        Cria uma instância de `kombu.Queue` com base nos argumentos informados
        durante a instanciação.
        """
        kwargs = {
            k: v
            for k, v in self._queue_init_kwargs.items()
            if v != UNDEFINED
        }
        if 'routing_key' not in kwargs:
            kwargs['routing_key'] = f'{self}.#'
        if 'exchange' not in kwargs:
            kwargs['exchange'] = self
        if 'queue_arguments' in kwargs:
            kwargs['queue_arguments'] = self._validate_queue_arguments(kwargs['queue_arguments'])

        return Queue(name=self, **kwargs)

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    @staticmethod
    def _create_queue_name(queue: str):
        return f'template-fastapi-celery.{queue}'

    @staticmethod
    def _validate_queue_arguments(queue_arguments: Any):
        if not queue_arguments:
            return queue_arguments
        elif isinstance(queue_arguments, QueueArguments):
            return queue_arguments.model_dump(by_alias=True)
        elif isinstance(queue_arguments, dict):
            return QueueArguments(**queue_arguments).model_dump(by_alias=True)
        elif isinstance(queue_arguments, object):
            return QueueArguments(**queue_arguments.__dict__).model_dump(by_alias=True)
        raise TypeError(queue_arguments)
