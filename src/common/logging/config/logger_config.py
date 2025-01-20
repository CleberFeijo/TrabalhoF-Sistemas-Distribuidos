from ._base import _BaseConfig

from ..enums import LevelEnum

__all__ = 'LoggerConfig',


class LoggerConfig(_BaseConfig):
    """
    Subclasse de dict, responsável por determinar os parâmetros
    (com suas respectivas anotações) das configurações possíveis de um Logger
    do módulo logging.

    - A instância desta classe pode ser utilizada como configuração do logging.
    """
    def __init__(
            self,
            level: LevelEnum | None = None,
            propagate: bool | None = None,
            filters: list[str] | None = None,
            handlers: list[str] | None = None,
    ):
        super().__init__(**{
            'level': level,
            'propagate': propagate,
            'filters': filters,
            'handlers': handlers,
        })
