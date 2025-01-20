from common.classes import Serializable

from ._serializer import *

__all__ = 'SerializableTypeSerializer',


class SerializableTypeSerializer(_Serializer[Serializable]):
    """
    Responsável por serializar instâncias de `common.classes.Serializable` e
    suas subclasses.
    """
    def _encode_method(self, value: Serializable):
        return value.json_serialize()

    def _decode_method_map(self):
        return {}
