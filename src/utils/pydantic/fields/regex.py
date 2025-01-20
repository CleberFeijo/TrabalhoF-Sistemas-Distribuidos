import re

from bson import Regex
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any

__all__ = 'RegexField',


def _flags_to_str(flags: int):
    _flag_map = {
        re.IGNORECASE: 'i',
        re.MULTILINE: 'm',
        re.VERBOSE: 'x',
        re.DOTALL: 's',
        re.UNICODE: 'u',
    }
    return ''.join(char for flag, char in _flag_map.items() if flags & flag)


class RegexField(Regex):
    """Field do pydantic para `bson.Regex`."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate(v):
            if isinstance(v, Regex):
                return v
            elif isinstance(v, str):
                return Regex(v)
            elif isinstance(v, dict):
                return Regex(**v)

        return core_schema.no_info_after_validator_function(
            function=validate,
            schema=core_schema.union_schema(
                choices=[
                    core_schema.is_instance_schema(Regex),
                    core_schema.str_schema(),
                    core_schema.typed_dict_schema(
                        fields={
                            'pattern': core_schema.typed_dict_field(
                                core_schema.str_schema()
                            ),
                            'flags': core_schema.typed_dict_field(
                                core_schema.str_schema(pattern=r'^[imsux]$')
                            ),
                        },
                        extra_behavior='forbid',
                    ),
                ],
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: {'pattern': x.pattern, 'flags': _flags_to_str(x.flags)},
                return_schema=core_schema.dict_schema(
                    keys_schema=core_schema.literal_schema(['pattern', 'flags']),
                    values_schema=core_schema.str_schema(),
                ),
                when_used='json',
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
            r'^\d+$',
            {'pattern': r'^\d+$', 'flags': 'gm'},
        ]
        return json_schema
