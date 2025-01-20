from bson import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Any

__all__ = 'ObjectIdField',


class ObjectIdField(ObjectId):
    """Field do pydantic para `bson.ObjectId`."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            _core_schema: core_schema.CoreSchema,
            handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(_core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = ['62fa9b2943223e5d0f002d7d']
        return json_schema

    @classmethod
    def validate(cls, v: Any, handler: GetCoreSchemaHandler):
        if isinstance(v, ObjectId):
            return v

        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)

        raise ValueError(f'{v} não é um ObjectId válido')
