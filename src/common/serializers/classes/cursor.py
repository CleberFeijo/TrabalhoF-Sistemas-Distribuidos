from abc import ABC
from pymongo.cursor import Cursor
from pymongo.command_cursor import CommandCursor

from common.typealiases import Generic, T

from ._serializer import *

__all__ = 'CursorSerializer', 'CommandCursorSerializer',


class _CursorLikeSerializer(_Serializer, ABC, Generic[T]):
    def _encode_method(self, value: T) -> list:
        return list(value)

    def _decode_method_map(self):
        return {}


class CursorSerializer(_CursorLikeSerializer[Cursor]):
    """Responsável por serializar instâncias de Cursor."""
    pass


class CommandCursorSerializer(_CursorLikeSerializer[CommandCursor]):
    """Responsável por serializar instâncias de CommandCursor."""
    pass
