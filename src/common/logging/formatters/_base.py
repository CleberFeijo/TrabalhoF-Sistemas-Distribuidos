import logging

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..enums import CC

__all__ = '_BaseFormatter', 'MessageFormat',


@dataclass
class MessageFormat:
    """
    Classe auxiliar usada para determinar os detalhes de formatação de uma
    mensagem.
    """
    prefix: Optional[str] = None
    message: Optional[str] = None
    suffix: Optional[str] = None
    color: Optional[CC] = None


class _BaseFormatterMeta(type(logging.Formatter)):

    def __new__(cls, *args, **kwargs):
        new_type = super().__new__(cls, *args, **kwargs)
        cls._set_formats(new_type)
        return new_type

    @staticmethod
    def _set_formats(new_type):
        new_formats: dict[int, MessageFormat] = {}

        for scls in new_type.__mro__:
            for level, fmt in getattr(scls, '__formats__', {}).items():
                if level not in new_formats:
                    new_formats[level] = fmt
                    continue

                for field in ('prefix', 'message', 'suffix'):
                    if getattr(new_formats[level], field) is not None:
                        continue
                    if getattr(fmt, field) is None:
                        continue
                    setattr(new_formats[level], field, getattr(fmt, field))

        setattr(new_type, '__formats__', new_formats)


class _BaseFormatter(logging.Formatter, metaclass=_BaseFormatterMeta):
    """
    Formatador de logging usado de base para criar outros formatadores de
    logging.

    - Deve implementar o método "default_format", retornando o formato padrão
      de mensagens a serem logadas, independente do nível do logging;
    - Deve implementar o atributo de classe "__formats__", contendo a
      correlação entre um nível de logging e um formato de mensagem;
    - Para cada campo não-preenchido ou de valor None de um "MessageFormat"
      definido em "__formats__", a metaclasse tentará definir o valor de acordo
      com um valor não-nulo definido em alguma superclasse.
    """

    __formats__: dict[int, MessageFormat] = {}
    """
    Deve conter a correlação de um nível específico de logging com sua
    respectiva formatação.

    - Valor de "MessageFormat" não preenchidos ou preenchidos com None
      utilizarão o respectivo valor da superclasse, caso exista.
    """

    @abstractmethod
    def default_format(self) -> MessageFormat:
        pass

    def _get_format(self, levelno: int, key: str):
        fmt = self.__formats__.get(levelno)
        if (value := getattr(fmt, key, None)) is not None:
            return value
        return getattr(self.default_format(), key, None)

    def get_prefix_format(self, levelno: int) -> str:
        return self._get_format(levelno, 'prefix') or ''

    def get_message_format(self, levelno: int) -> str:
        return self._get_format(levelno, 'message') or ''

    def get_suffix_format(self, levelno: int) -> str:
        return self._get_format(levelno, 'suffix') or ''

    def get_color(self, leveno: int) -> Optional[CC]:
        return self._get_format(leveno, 'color') or None

    def get_format(self, levelno: int = logging.INFO) -> str:
        fmts = [
            self.get_prefix_format(levelno),
            self.get_message_format(levelno),
            self.get_suffix_format(levelno),
        ]
        fmt = " ".join([f for f in fmts if f])

        if color := self.get_color(levelno):
            fmt = f'{color}{fmt}{CC.RESET}'

        return fmt

    def format(self, record: logging.LogRecord):
        return logging.Formatter(
            fmt=self.get_format(record.levelno),
            datefmt=self.datefmt,
        ).format(record)
