from bson import ObjectId, Regex
from datetime import date, datetime
from typing import Any

from common.classes import Undefined

from .json_encoder import JSONEncoder

from ..classes import DateTimeSerializer

__all__ = 'MongoEncoder',


class MongoEncoder:
    """
    Pseudo-encoder para tratar/validar objetos antes de serem
    inseridos/atualizados/substituídos em uma coleção do MongoDB.

    - Não é uma subclasse de "json.JSONEncoder" pois entra em loop infinito
      em alguns casos;
    - Remove os campos com valor igual a Undefined;
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, dict):
            return {
                self.default(k): self.default(v)
                for k, v in o.items()
                if not isinstance(v, Undefined) and not v == Undefined
            }
        elif isinstance(o, (list, set, tuple)):
            return [
                self.default(x)
                for x in o
                if not isinstance(x, Undefined) and not x == Undefined
            ]
        elif isinstance(o, (ObjectId, datetime, Regex)):
            return o
        elif isinstance(o, date):
            return DateTimeSerializer().decode(o)

        try:
            from utils.pymongo import MongoModel
            if isinstance(o, MongoModel):
                return o.mongo_serialize()
        except ImportError:
            pass

        return JSONEncoder().dump(o)

    def dump(self, o):
        return self.default(o)
