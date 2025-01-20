from .serializable import Serializable

__all__ = 'Undefined', 'UNDEFINED',


class Undefined(Serializable):
    """
    Classe usada para definir uma variável como vazia (ou não preenchida),
    normalmente quando o valor `None` for um valor válido.

    Comumente usado junto ao "MongoModel", para remover o campo durante
    a serialização (antes de salvar no mongodb, por exemplo).

    - Possui valor lógico equivalente a `False`;
    - É convertido para `None` quando serializado;
    """
    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, self.__class__) or other is self.__class__

    def json_serialize(self):
        return None


UNDEFINED = Undefined()
"""
Singleton usado para definir uma variável como vazia (ou não preenchida),
normalmente quando o valor `None` for um valor válido.

Comumente usado junto ao "MongoModel", para remover o campo durante
a serialização (antes de salvar no mongodb, por exemplo).

- Possui valor lógico equivalente a `False`;
- É convertido para `None` quando serializado;
"""
