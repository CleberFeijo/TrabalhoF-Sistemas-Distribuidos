from enum import Enum, IntEnum

from ._serializer import *

__all__ = 'EnumSerializer', 'IntEnumSerializer',


class EnumSerializer(_Serializer[Enum]):
    """
    Responsável por serializar instâncias de Enum e suas subclasses.

    - `aenum.Enum` é uma subclasse de `enum.Enum`;
    - Não é capaz de realizar "decode" por servir como uma classe de base;
    """
    def _encode_method(self, value: Enum) -> str:
        return value.value

    def _decode_method_map(self):
        return {}


class IntEnumSerializer(_Serializer[IntEnum]):
    """
    Responsável por serializar instâncias de IntEnum e suas subclasses.

    - Não é capaz de realizar "decode" por servir como uma classe de base;
    """
    def _encode_method(self, value: IntEnum) -> int:
        return value.value

    def _decode_method_map(self):
        return {}
