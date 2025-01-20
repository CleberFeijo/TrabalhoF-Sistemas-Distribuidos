import logging

from abc import ABC
from celery.app.task import Task as CeleryTask
from typing import Optional, Union

from ..functions import get_auto_retry_exceptions

__all__ = 'Task',


class Task(CeleryTask, ABC):
    """
    Classe que extende `celery.app.task.Task`, usada de base na criação de
    outras tarefas, adicionando também vínculo com um logger próprio e os
    métodos de logar as mensagens.

    Contém algumas configurações genéricas compartilhadas por todas as tarefas.
    """
    autoretry_for = tuple(get_auto_retry_exceptions())
    """
    Iterável contendo as classes das exceções que indicam que uma tarefa pode
    ser reenfileirada em caso de sua ocorrência.
    """

    max_retries: Optional[int] = None
    """
    Número máximo de retentativas de execução de uma tarefa.
    None indica que não há um limite máximo.

    - O celery utiliza o valor padrão: 3.
    """

    retry_backoff: Union[int, bool] = 5
    """
    Determina o delay (em segundos) usado para a 'Espera Exponencial'
    (Exponential backoff) da retentativa de execução da tarefa.
    Quando True, utiliza o valor 1.
    Quando False, não possui espera exponencial.

    - O celery utiliza o valor padrão: False.
    """

    retry_backoff_max: int = 600
    """
    Determina o máximo de delay acumulado pela 'Espera Exponencial'.

    - O celery utiliza o valor padrão: 600.
    """

    retry_jitter: bool = False
    """
    Quando True, adiciona um nível de aleatoriadade para o acúmulo da
    'Espera Exponencial', visando previnir que todas as tarefas sejam
    reenfileiradas para o mesmo horário.

    - O celery utiliza o valor padrão: True.
    """

    logger: Optional[logging.Logger] = None
    """
    Permite vincular um logger a tarefa, permitindo o output das mensagens
    logadas durante a execução da tarefa.
    """

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def run(self, *args, **kwargs):
        pass

    def before_start(self, task_id, args, kwargs):
        self.info(f'Tarefa "{task_id}" iniciada! [args: {args}, kwargs: {kwargs}]')
        super().before_start(task_id, args, kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        self.info(f'Tarefa "{task_id}" concluída com sucesso! [args: {args}, kwargs: {kwargs}]')
        super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.error(f'Tarefa "{task_id}" falhou! [args: {args}, kwargs: {kwargs}]')
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pass

    def debug(self, *msg: str):
        self._log(*msg, level=logging.DEBUG)

    def info(self, *msg: str):
        self._log(*msg, level=logging.INFO)

    def warning(self, *msg: str):
        self._log(*msg, level=logging.WARNING)

    def error(self, *msg: str):
        self._log(*msg, level=logging.ERROR)

    def critical(self, *msg: str):
        self._log(*msg, level=logging.CRITICAL)

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    def _log(self, *msg: str, level: int):
        if self.logger:
            self.logger.log(level=level, msg=' '.join([str(m) for m in msg]))
