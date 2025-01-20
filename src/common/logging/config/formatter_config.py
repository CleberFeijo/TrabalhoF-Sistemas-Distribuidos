from typing import Optional, Union

from common.enums import DateStringEnum

from ._base import _BaseConfig

__all__ = 'FormatterConfig',


class FormatterConfig(_BaseConfig):
    """
    Subclasse de dict, responsável por determinar os parâmetros (com suas
    respectivas anotações) das configurações possíveis de um Formatter do
    módulo logging.

    - A instância desta classe pode ser utilizada como configuração do logging.
    """
    def __init__(
            self,
            cls: Union[str, type, None] = None,
            fmt: Optional[str] = None,
            datefmt: Optional[DateStringEnum] = None,
            style: Optional[str] = None,
            validate: Optional[bool] = None,
            **kwargs
    ):
        if cls is None and 'class' in kwargs:
            cls = kwargs['class']
        if fmt is None and 'format' in kwargs:
            fmt = kwargs['format']
        if isinstance(cls, type):
            cls = f'{cls.__module__}.{cls.__qualname__}'

        super().__init__(**{
            'class': cls,
            'format': fmt,
            'datefmt': datefmt,
            'style': style,
            'validate': validate,
        })
