from common.classes import ModuleIterator
from common.typealiases import Iterator, Type, TypeVar, Union

from ..classes import SerializerT

__all__ = 'Decoder',

InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')


class _DecoderMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        import common.serializers.classes as serializers
        attrs['__serializers__'] = tuple(
            s()
            for s in ModuleIterator(serializers).it_classes(deep_search=False)
            if s().can_decode
        )
        return super().__new__(mcs, name, bases, attrs, **kwargs)


class Decoder(metaclass=_DecoderMeta):
    """
    Decoder genérico.

    Utiliza as subclasses do tipo `SerializerT` contidas em
    `common.serializers.classes` para realizar o *decoding*.

    - O campo `__serializers__` é definido pela metaclasse.
    - Não extende `json.JSONDecoder`, pois não realiza o decode de objetos
      aninhados e o decode pode ser realizado de um tipo python para outro tipo
      python.
    """

    __serializers__: tuple[SerializerT, ...]
    "Tupla contendo os serializers importados do módulo relativo 'classes'."

    def load(
            self,
            input_value: InputT,
            output_type: Type[OutputT],
    ) -> Union[InputT, OutputT]:
        """
        Tenta realizar o decode do valor informado para o tipo solicitado.

        - Caso não consiga realizar o decode, retorna o próprio tipo informado!

        :param input_value: Valor a ser decodificado;
        :param output_type: Tipo a ser retornado;
        """
        if isinstance(input_value, output_type):
            return input_value

        # Tenta usar o serializer EXATO para o tipo determinado.
        for serializer in self._it_serializers():
            if output_type == serializer.type:
                try:
                    return serializer.decode(input_value)
                except Exception:  # noqa
                    break

        # Caso não consiga, tenta o primeiro serializer que pode tratar o tipo
        # informado.
        for serializer in self._it_serializers():
            if serializer.typecheck(output_type):
                try:
                    return serializer.decode(input_value)
                except Exception:  # noqa
                    pass

        # Retorna o valor informado caso não consiga realizar o decode.
        return input_value

    # ========================= #
    # ~~~~| Class Methods |~~~~ #
    # ========================= #

    @classmethod
    def decoding_types(cls) -> tuple[type, ...]:
        """
        Retorna uma tupla contendo todos os tipos que são passíveis de
        *decoding* por esta instância.
        """
        return tuple(s.type for s in cls._it_serializers() if s.type)

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    @classmethod
    def _it_serializers(cls) -> Iterator[SerializerT]:
        yield from cls.__serializers__
