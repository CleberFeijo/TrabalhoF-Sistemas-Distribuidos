from aenum import StrEnum
from datetime import date, datetime
from typing import Type, TypeVar

__all__ = 'DateStringEnum',

DateT = TypeVar('DateT', date, datetime)


class DateStringEnum(StrEnum):
    """
    Subclasse de `aenum.StrEnum` contendo os formatos de data válidos mais
    utilizados.
    """
    DATE_FORMAT = '%Y-%m-%d'
    """Formato padrão para `datetime.date`."""

    DATE_BR_FORMAT = '%d/%m/%Y'
    """Formato BR para `datetime.date`."""

    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    """Formato padrão para `datetime.datetime`."""

    DATETIME_BR_FORMAT = '%d/%m/%Y %H:%M:%S'
    """Formato BR para `datetime.datetime`."""

    DATETIME_FILE_FORMAT = '%Y-%m-%d-%H-%M-%S'
    """Formato para `datetime.datetime` para nome de arquivos."""

    DATETIME_SOLR_FORMAT = '%Y-%m-%dT%H:%M:%S'
    """Formato para date/datetime para consulta no solr."""

    DATETIME_FULL_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
    """
    Formato para `datetime.datetime` completo (com microssegundos mas sem timezone).
    """

    DATETIME_FULL_TZ_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
    """
    Formato para `datetime.datetime` completo (com microssegundos e timezone).
    """

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def format_dt(self, dt: DateT) -> str:
        """Equivalente à dt.strftime(self)."""
        return dt.strftime(self)

    def parse_dt(self, s: str, type_: Type[DateT] = datetime) -> DateT:
        """
        Equivalente a `datetime.strptime(s, self)` ou
        `datetime.strptime(s, self).date()`, de acordo com o tipo de retorno
        informado.

        :param s: string a ser parseada;
        :param type_: Informa o tipo a ser retornado, date ou datetime;
        """
        dt = datetime.strptime(s, self)
        return dt if type_ == datetime else dt.date()
