from dataclasses import is_dataclass
from typing import Any

from ._serializer import *

__all__ = 'DataclassSerializer',


class DataclassSerializer(_Serializer):
    """
    Responsável por serializar instâncias de classes envelopadas por
    `@dataclasses.dataclass`.
    """

    def typecheck(self, value: Any) -> bool:
        return is_dataclass(value)

    def _encode_method(self, value) -> dict[str, Any]:
        return value.__dict__

    def _decode_method_map(self):
        return {}
