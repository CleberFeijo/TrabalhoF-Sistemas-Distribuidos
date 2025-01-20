from typing import Optional, Union

from ._base import _BaseConfig

from ..enums import LevelEnum

__all__ = 'HandlerConfig',


class HandlerConfig(_BaseConfig):
    """
    Subclasse de dict, responsável por determinar os parâmetros (com suas
    respectivas anotações) das configurações possíveis de um Handler do
    módulo logging.

    - A instância desta classe pode ser utilizada como configuração do logging.
    """
    def __init__(
            self,
            cls: Union[str, type, None] = None,
            level: Optional[LevelEnum] = None,
            formatter: Optional[str] = None,
            filters: Optional[list[str]] = None,
            **kwargs
    ):
        """
        Cria o dict contendo os parâmetros de configuração usados pelo logging.

        - Todos os kwargs são enviados para instanciação da classe Handler,
          exceto "class", que serve como um alias para cls.

        :param cls: Classe (ou caminho) da classe de "Handler";
        :param formatter: Nome da chave do formatador definido na chave
            "formatters" da config do logging;
        :param level: Nível de logging do handler;
        :param filters: Lista das chaves dos filtros definidos na chave
            "filters" da config do logging;
        """
        if 'class' in kwargs:
            cls = kwargs.pop('class')
        if cls is None:
            raise ValueError('cls ou class deve ser informado.')
        if isinstance(cls, type):
            cls = f'{cls.__module__}.{cls.__qualname__}'

        super().__init__(**{
            'class': cls,
            'level': level,
            'formatter': formatter,
            'filters': filters,
            **kwargs,
        })
