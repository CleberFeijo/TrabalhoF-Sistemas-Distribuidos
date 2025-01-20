from bson import ObjectId
from datetime import date, datetime

from common.enums import DateStringEnum

from ._serializer import *

__all__ = 'DateSerializer',


class DateSerializer(_Serializer[date]):
    """Responsável por serializar/deserializar instâncias de date."""

    def _encode_method(self, value: date) -> str:
        return value.strftime(DateStringEnum.DATE_FORMAT)

    def _decode_method_map(self):
        return {
            str: self._str_to_date,
            datetime: self._datetime_to_date,
            ObjectId: self._oid_to_date,
        }

    @staticmethod
    def _str_to_date(s: str) -> date:
        dt_str: DateStringEnum
        for dt_str in DateStringEnum:
            try:
                return dt_str.parse_dt(s, date)
            except ValueError:
                pass

        raise ValueError(f'{s} não possui um dos formatos de data válidos. '
                         f'Formatos válidos: {list(DateStringEnum)}')

    @staticmethod
    def _datetime_to_date(d: datetime) -> date:
        return d.date()

    @staticmethod
    def _oid_to_date(o: ObjectId) -> date:
        return o.generation_time.astimezone().date()
