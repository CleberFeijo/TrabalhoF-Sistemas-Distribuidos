from abc import ABC

__all__ = 'Serializable',


class Serializable(ABC):
    """
    Classe abstrata usada para definir uma classe como serializável.

    - O encoder utiliza o método `self.json_serialize` desta classe para fazer
      a serialização.
    - Por padrão, o método `self.json_serialize` retorna `self.__dict__`,
      mas pode ser sobrescrito na subclasse, devendo retornar um objeto
      serializável.
    """
    def json_serialize(self):
        """Serializa a instância para um formato JSON válido."""
        return self.__dict__
