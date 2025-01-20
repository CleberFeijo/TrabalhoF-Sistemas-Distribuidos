from celery.schedules import crontab
from datetime import timedelta
from typing import Iterable, Optional, Sequence, Union

from common.classes import UNDEFINED

__all__ = 'BeatSchedule',


class BeatSchedule(dict):
    """
    Subclasse de dict contendo os campos válidos para a config de
    "beat_schedule" do celery.
    """

    # noinspection PyUnusedLocal
    # OBS: valores são acessados através do vars()
    def __init__(
            self,
            *,
            task: str,
            schedule: Union[int, timedelta, crontab],
            args: Optional[Sequence] = UNDEFINED,
            kwargs: Optional[dict] = UNDEFINED,
            options: Optional[dict] = UNDEFINED,
            relative: bool = UNDEFINED,
    ):
        """
        :param task:
            Nome da tarefa que será executada.

        :param schedule:
            Frequência da execução da tarefa.
            Valores inteiros indicam a recorrência em segundos.

        :param args:
            Argumentos posicionais passados para a tarefa.

        :param kwargs:
            Argumentos nomeados passados para a tarefa.

        :param options:
            Opções de execução - aceita os mesmos argumentos que `.apply_async`.

        :param relative:
            Quando `True`, indica que a frequência de execução é contada a
            partir da data de execução da última tarefa;
            Caso contrário, indica que é contada a partir da data de
            inicialização do worker.
        """
        super().__init__({
            k: v
            for k, v in vars().items()
            if k != 'self' and not k.startswith('_') and v != UNDEFINED
        })

    @classmethod
    def create_schedules(
            cls,
            schedules: Iterable['BeatSchedule'],
    ) -> dict[str, 'BeatSchedule']:
        """
        Cria um dict no formato aceito pela config "beat_schedule" do celery,
        utilizando os schedules recebidos.
        """
        return {s['task']: s for s in schedules}
