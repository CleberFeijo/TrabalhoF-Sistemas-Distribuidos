from common.classes import ModuleIterator
from common.typealiases import Iterable, Iterator, ModuleT

from ..hooks import PytestHook

__all__ = 'it_hooks',


def it_hooks(*path) -> Iterator[PytestHook]:
    """
    Função responsável por iterar quaisquer iterável recebido, criando um
    generator com os hooks do pytest encontrados.
    """
    for x in path:
        if isinstance(x, dict):
            yield from it_hooks(*x.values())
        elif isinstance(x, ModuleT):
            yield from it_hooks(
                *ModuleIterator(x).it_classes(subclass_of=PytestHook),
                *ModuleIterator(x).it_instances(instance_of=PytestHook),
            )
        elif isinstance(x, PytestHook):
            yield x
        elif isinstance(x, type) and issubclass(x, PytestHook):
            yield x()
        elif isinstance(x, Iterable) and not isinstance(x, str):
            yield from it_hooks(*x)
