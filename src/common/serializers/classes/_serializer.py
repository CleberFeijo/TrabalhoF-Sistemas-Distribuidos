from abc import ABC, ABCMeta, abstractmethod

from common.classes import GenericMeta
from common.typealiases import Any, Callable, Generic, T, Type, TypeVar

__all__ = '_Serializer', 'SerializerT',

SerializerT = TypeVar('SerializerT', bound='_Serializer')
SerializableT = TypeVar('SerializableT')


class _SerializerMeta(GenericMeta, ABCMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):
        attrs['__type__'] = mcs._get_generic_param(attrs)
        return super().__new__(mcs, name, bases, attrs, **kwargs)


class _Serializer(ABC, Generic[SerializableT], metaclass=_SerializerMeta):
    """
    Classe de base genérica, responsável por criar um serializer/deserializer
    para o tipo determinado.

    Toda subclasse é capaz de realizar o *encode* do tipo anotado, mas nem toda
    subclasse é capaz de realizar o *decode*.

    - O campo `__type__` é definido com base no tipo genérico anotado!
    """
    __type__: Type[SerializableT]

    # ====================== #
    # ~~~~| Properties |~~~~ #
    # ====================== #

    @property
    def type(self):
        """Retorna o tipo que essa classe envelopa."""
        return self.__type__

    @property
    def decoding_types(self):
        """Retorna os tipos que essa classe é capaz de realizar o decode."""
        return tuple(self._decode_method_map().keys())

    @property
    def can_decode(self):
        """Determina se essa classe pode realizar decode para o tipo anotado."""
        return bool(self.decoding_types)

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def typecheck(self, value: Any) -> bool:
        """
        Checa se o valor informado pode ser ser serializado por esta classe.

        :param value: Valor a ser checado;
        """
        if isinstance(value, self.__type__):
            return True
        try:
            return issubclass(value, self.__type__)
        except TypeError:
            return False

    def encode(self, value: SerializableT):
        """
        Método responsável por converter o valor recebido, que deve ser do tipo
        genérico desta classe, para um formato JSON válido.

        :param value: Valor a ser convertido.
        """
        if not self.typecheck(value):
            raise TypeError(f'{value} não é do tipo {self.__type__}.')
        return self._encode_method(value)

    def decode(self, value: Any) -> SerializableT:
        """
        Método responsável por converter o valor recebido para o tipo genérico
        desta classe.

        :param value: Valor a ser convertido.
        :return:
        """
        _map = self._decode_method_map()

        # Tenta realizar a conversão pelo tipo EXATO.
        if type(value) in _map:
            return _map[type(value)](value)

        # Caso não consiga, tenta converter em caso de subclasse do tipo mapeado.
        for t, func in _map.items():
            if isinstance(value, t):
                return func(value)

        raise ValueError(f'Valor informado é do tipo {type(value)}, que não '
                         f'pode ser convertido no tipo {self.__type__}.')

    # ============================ #
    # ~~~~| Abstract Methods |~~~~ #
    # ============================ #

    @abstractmethod
    def _encode_method(self, value: SerializableT):
        """Converte o valor recebido em um tipo JSON válido."""
        pass

    @abstractmethod
    def _decode_method_map(self) -> dict[Type[T], Callable[[T], SerializableT]]:
        """
        Retorna a correlação de um tipo com o respectivo método de conversão
        para o tipo genérico desta classe.
        """
        pass
