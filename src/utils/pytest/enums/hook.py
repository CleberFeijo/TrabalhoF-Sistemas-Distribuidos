from aenum import LowerStrEnum, auto

__all__ = 'PytestHookEnum',


class PytestHookEnum(LowerStrEnum):
    """
    Subclasse de `aenum.LowerStrEnum` contendo os eventos chamados pelo arquivo
    `conftest.py`, usado pelo pytest.
    """
    CONFIGURE = auto()
    SESSIONSTART = auto()
    SESSIONFINISH = auto()
    UNCONFIGURE = auto()
