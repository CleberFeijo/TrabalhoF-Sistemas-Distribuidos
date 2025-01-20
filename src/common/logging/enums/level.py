import logging

from aenum import UpperStrEnum, auto

__all__ = 'LevelEnum',


class LevelEnum(UpperStrEnum):
    """
    Subclasse de `aenum.UpperStrEnum` contendo os possíveis níveis de logging.

    - Pode ser convertido para int, retornando o respectivo valor numérico
      utilizado pelo logging.
    """
    NOTSET = auto()
    DEBUG = auto()
    INFO = auto()
    WARN = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()
    FATAL = auto()

    def __int__(self):
        cls = self.__class__
        return {
            cls.NOTSET: logging.NOTSET,
            cls.DEBUG: logging.DEBUG,
            cls.INFO: logging.INFO,
            cls.WARN: logging.WARN,
            cls.WARNING: logging.WARNING,
            cls.ERROR: logging.ERROR,
            cls.CRITICAL: logging.CRITICAL,
            cls.FATAL: logging.FATAL,
        }.get(self)
