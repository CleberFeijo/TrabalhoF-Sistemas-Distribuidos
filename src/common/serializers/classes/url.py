from pydantic.networks import Url  # noqa

from ._serializer import *

__all__ = 'UrlSerializer',


class UrlSerializer(_Serializer[Url]):
    """Responsável por serializar/deserializar instâncias de `bson.ObjectId`."""

    def _encode_method(self, value: Url) -> str:
        return str(value)

    def _decode_method_map(self):
        return {}
