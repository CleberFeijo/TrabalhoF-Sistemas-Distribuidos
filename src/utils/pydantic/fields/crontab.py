import re

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any

__all__ = 'CrontabStringField',

RE_BASE = r'(\*|({regex}(?!\d)|(?<=\d)[-,]{regex}|(\*|{regex})\/(?=\d))+)'

RE_MINUTE = RE_BASE.format(regex=r'[0-5]?[0-9]')
RE_HOUR = RE_BASE.format(regex=r'([01]?[0-9]|2[0-3])')
RE_DAY_OF_MONTH = RE_BASE.format(regex=r'([012]?[0-9]|3[01])')
RE_DAY_OF_WEEK = RE_BASE.format(regex=r'([0-7]|SUN|MON|TUE|WED|THU|FRI|SAT)')
RE_MONTH_OF_YEAR = RE_BASE.format(regex=r'(0?[1-9]|1[012]|JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)')


class CrontabStringField(str):
    """Field do pydantic para strings no formato do "crontab"."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.str_schema(
            pattern=re.compile(
                r'^{} +{} +{} +{} +{}$'.format(
                    RE_MINUTE,
                    RE_HOUR,
                    RE_DAY_OF_MONTH,
                    RE_MONTH_OF_YEAR,
                    RE_DAY_OF_WEEK,
                ),
                flags=re.I,
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            _core_schema: core_schema.CoreSchema,
            handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(_core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = [
            '* * * * *',
            '0 4 8-14 * *',
            '5 4 * * SUN',
        ]
        return json_schema
