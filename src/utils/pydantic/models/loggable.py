import logging

from typing import Optional

from common.classes import UNDEFINED

from .base import BaseModel

__all__ = 'LoggableModel',


class LoggableModel(BaseModel):
    """
    Subclasse de `utils.pydantic.BaseModel` responsável por conter o campo
    determinando o Logger utilizado para output de mensagens e os respectivos
    métodos para utilização deste logger com redução de verbosidade.

    - Caso o logger não seja informado, utiliza a função `print`.
    - Caso informe o valor None, desabilita o output de logs.
    """

    logger: Optional[logging.Logger] = UNDEFINED
    """
    Determina o logger usado para realizar os logs.

    - Informar valor "None" impede o output de logs;
    - Não informar valor utiliza o método padrão "print".
    """

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

    def _log(self, *msg: str, level: int):
        if self.logger:
            self.logger.log(level=level, msg=' '.join([str(m) for m in msg]))
        elif self.logger == UNDEFINED:
            print(msg)
