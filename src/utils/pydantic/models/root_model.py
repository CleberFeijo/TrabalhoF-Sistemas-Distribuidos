from pydantic import RootModel as PydanticRootModel

from .base import BaseModel

__all__ = 'RootModel',


class RootModel(PydanticRootModel):
    """
    Subclasse de `pydantic.RootModel` que implementa uma lógica similar
    à de "Custom Root Type", com algumas mudanças:

    - Implementa as configs do modelo de base.
    - Atualiza o método `__str__`.
    """
    # Extende as configurações do BaseModel.
    # noinspection Pydantic
    model_config = {
        k: v
        for k, v in BaseModel.model_config.items()
        if k not in ('extra',)
    }

    def __str__(self):
        return super().__str__().replace('root=', '')
