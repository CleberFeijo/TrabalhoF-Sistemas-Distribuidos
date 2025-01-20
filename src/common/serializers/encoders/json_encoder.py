from json import JSONEncoder as BaseJSONEncoder, loads
from typing import Any, Iterator

from common.classes import ModuleIterator, Serializable

from ..classes import SerializerT

__all__ = 'JSONEncoder',


class _JSONEncoderMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        import common.serializers.classes as serializers
        attrs['__serializers__'] = tuple(
            s()
            for s in ModuleIterator(serializers).it_classes(deep_search=False)
        )
        return super().__new__(mcs, name, bases, attrs, **kwargs)


class JSONEncoder(BaseJSONEncoder, metaclass=_JSONEncoderMeta):
    """
    Encoder genérico, extendido de `json.JSONEncoder`.

    Utiliza as subclasses do tipo `SerializerT` contidas em
    `common.serializers.classes` para realizar o *encoding*.

    - O campo `__serializers__` é definido pela metaclasse.
    - Também trata a classe `common.classes.serializable.Serializable`;
    """

    __serializers__: tuple[SerializerT, ...]
    "Tupla contendo serializers importados do módulo relativo 'classes'."

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def default(self, o: Any) -> Any:
        if isinstance(o, Serializable):
            return o.json_serialize()

        # Tenta usar o serializer EXATO para o tipo determinado.
        for serializer in self._it_serializers():
            if type(o) is serializer.type:
                return serializer.encode(o)

        # Caso não consiga, tenta o primeiro serializer que pode tratar o tipo
        # informado.
        for serializer in self._it_serializers():
            if serializer.typecheck(o):
                return serializer.encode(o)

        return super().default(o)

    def dump(self, o):
        """
        Converte um objeto python para outro objeto python, alterando
        os campos contidos no objeto original para um formato que possa
        ser serializável para JSON.

        - Alias para "`json.loads(self.encode(o))`";
        """
        return loads(self.encode(o))

    # ========================= #
    # ~~~~| Class Methods |~~~~ #
    # ========================= #

    @classmethod
    def encoding_types(cls) -> tuple[type, ...]:
        """
        Retorna uma tupla contendo todos os tipos que são passíveis de
        *encoding* por esta instância.
        """
        return tuple(s.type for s in cls._it_serializers() if s.type)

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    @classmethod
    def _it_serializers(cls) -> Iterator[SerializerT]:
        yield from cls.__serializers__
