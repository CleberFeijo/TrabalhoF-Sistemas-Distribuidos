from bson import Regex
from typing import Any

from ._serializer import *

__all__ = 'RegexSerializer',


class RegexSerializer(_Serializer[Regex]):
    """
    Responsável por serializar/deserializar instâncias de `bson.regex.Regex`.
    """
    def _encode_method(self, value: Regex) -> dict[str, Any]:
        return {'pattern': value.pattern, 'flags': value.flags}

    def _decode_method_map(self):
        return {
            str: Regex,
            dict: lambda x: Regex(**x),
        }
