from pydantic import BaseModel
from typing import Type

__all__ = 'is_root_model',


def is_root_model(Model: Type[BaseModel]) -> bool:
    """Checa se a classe informada utiliza o formato "Custom Root Type"."""
    return '__root__' in Model.__fields__
