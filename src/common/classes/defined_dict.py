from .undefined import UNDEFINED

__all__ = 'DefinedDict',


class DefinedDict(dict):
    """
    Subclasse de `dict` que impede a inserção de dados de valor "UNDEFINED".
    """

    def __init__(self, d=None, /, **kwargs):
        init_kwargs = {}

        if d and isinstance(d, dict):
            init_kwargs.update(d)

        init_kwargs.update(kwargs)

        super().__init__(**{k: v for k, v in init_kwargs.items() if v != UNDEFINED})

    def __setitem__(self, key, value):
        if value != UNDEFINED:
            super().__setitem__(key, value)
