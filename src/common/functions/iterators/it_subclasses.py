from common.typealiases import Iterator, Type, T

__all__ = 'it_subclasses',


def it_subclasses(cls: Type[T], skip_abstract: bool = True) -> Iterator[Type[T]]:
    """
    Cria um iterador contendo todas as subclasses da classe informada.

    - Não retorna subclasses privadas.
    - Utiliza recursividade para capturar subclasses de subclasses.

    :param cls: Classe original que terá as subclasses iteradas;
    :param skip_abstract: Quando True, deixa de retornar as subclasses que
        não implementaram todos os métodos abstratos;
    """
    for subclass in cls.__subclasses__():
        if subclass.__name__.startswith('_'):
            continue
        if skip_abstract and getattr(subclass, '__abstractmethods__', None):
            continue

        yield subclass
        yield from it_subclasses(subclass, skip_abstract)
