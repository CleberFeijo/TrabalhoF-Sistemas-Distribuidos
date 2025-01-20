from bson import ObjectId
from datetime import date, datetime

from common.enums import DateStringEnum

from ._serializer import *

__all__ = 'DateTimeSerializer',


class DateTimeSerializer(_Serializer[datetime]):
    """Responsável por serializar/deserializar instâncias de datetime."""

    def _encode_method(self, value: datetime) -> str:
        return value.strftime(DateStringEnum.DATETIME_FORMAT)

    def _decode_method_map(self):
        return {
            str: self._str_to_datetime,
            date: self._date_to_datetime,
            ObjectId: self._oid_to_datetime,
        }

    @staticmethod
    def _str_to_datetime(s: str):
        dt_str: DateStringEnum
        for dt_str in DateStringEnum:
            try:
                return dt_str.parse_dt(s, datetime)
            except ValueError:
                pass

        raise ValueError(f'{s} não possui um dos formatos de data válidos. '
                         f'Formatos válidos: {list(DateStringEnum)}')

    @staticmethod
    def _date_to_datetime(d: date) -> datetime:
        return datetime.combine(d, datetime.min.time())

    @staticmethod
    def _oid_to_datetime(o: ObjectId) -> datetime:
        return o.generation_time.astimezone()
