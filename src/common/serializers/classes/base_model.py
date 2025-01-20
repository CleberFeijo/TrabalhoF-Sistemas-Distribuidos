from pydantic import BaseModel

from ._serializer import *

__all__ = 'BaseModelSerializer',


class BaseModelSerializer(_Serializer[BaseModel]):
    """
    Responsável por serializar instâncias de `pydantic.BaseModel`.

    - Trata diferentemente instâncias de "RootModel" do pydantic.
    """
    def _encode_method(self, value: BaseModel) -> dict | list:
        # Tratativa para "RootModel":
        if value.__class__.__dict__.get('__pydantic_root_model__', False):
            return getattr(value, 'root')

        # Retorno do BaseModel genérico.
        return value.model_dump()

    def _decode_method_map(self):
        return {}
