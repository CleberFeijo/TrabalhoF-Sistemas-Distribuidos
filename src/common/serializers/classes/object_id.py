from bson import ObjectId
from datetime import datetime

from ._serializer import *

__all__ = 'ObjectIdSerializer',


class ObjectIdSerializer(_Serializer[ObjectId]):
    """Responsável por serializar/deserializar instâncias de `bson.ObjectId`."""

    def _encode_method(self, value: ObjectId) -> str:
        return str(value)

    def _decode_method_map(self):
        return {
            str: ObjectId,
            datetime: ObjectId.from_datetime,
        }
