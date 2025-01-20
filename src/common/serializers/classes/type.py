from ._serializer import *

__all__ = 'TypeSerializer',


class TypeSerializer(_Serializer[type]):
    """Responsável por serializar instâncias de type (Classes)."""

    def _encode_method(self, value: type) -> str:
        return value.__name__

    def _decode_method_map(self):
        return {}
