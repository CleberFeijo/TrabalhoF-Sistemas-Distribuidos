from abc import ABC
from collections import deque

from common.typealiases import Generic, Iterable, T

from ._serializer import *

__all__ = 'DequeSerializer', 'SetSerializer', 'TupleSerializer',


class _IterableSerializer(_Serializer, ABC, Generic[T]):
    def _encode_method(self, value: T) -> list:
        return list(value)

    def _decode_method_map(self):
        return {
            Iterable: lambda x: self.__type__(x),
        }


class DequeSerializer(_IterableSerializer[deque]):
    """Responsável por serializar/deserializar instâncias de `deque`."""
    pass


class SetSerializer(_IterableSerializer[set]):
    """Responsável por serializar/deserializar instâncias de `set`."""
    pass


class TupleSerializer(_IterableSerializer[tuple]):
    """Responsável por serializar/deserializar instâncias de `tuple`."""
    pass
