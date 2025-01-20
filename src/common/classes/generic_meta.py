from types import GenericAlias
from typing import get_args, _GenericAlias  # noqa

__all__ = 'GenericMeta',


class GenericMeta(type):
    """
    Metaclasse usada junto com classes Generic, adicionando algumas
    funcionalidades que costumam ser utilizadas junto com o magic method __new__.
    """

    @staticmethod
    def _get_generic_param(attrs: dict):
        """Captura o tipo anotado pela classe genérica."""
        for base in attrs.get('__orig_bases__', []):
            for arg in get_args(base):
                if issubclass(type(arg), (type, GenericAlias, _GenericAlias)):
                    return arg
        return None
