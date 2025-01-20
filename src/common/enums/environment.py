from aenum import UpperStrEnum

__all__ = 'EnvEnum',


class EnvEnum(UpperStrEnum):
    """
    Subclasse de `aenum.UpperStrEnum`, usada para determinar o tipo de ambiente
    que a aplicação está rodando.
    """
    D = DEV = DEVELOP = 'DEV'
    "Ambiente de desenvolvimento (local)."

    H = HMLG = HOMOLOG = 'HOMOLOG'
    "Ambiente de homologação."

    P = PROD = PRODUCTION = 'PRODUCTION'
    "Ambiente de produção."

    @classmethod
    def _missing_(cls, value):
        return cls.__members__.get(value, None)

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def is_dev(self) -> bool:
        """
        Checa se está em ambiente de desenvolvimento - usado apenas para
        reduzir verbosidade de uma checagem por igualdade.
        """
        return self == self.__class__.D

    def is_hmlg(self) -> bool:
        """
        Checa se está em ambiente de homologação - usado apenas para
        reduzir verbosidade de uma checagem por igualdade.
        """
        return self == self.__class__.H

    def is_prod(self) -> bool:
        """
        Checa se está em ambiente de produção - usado apenas para
        reduzir verbosidade de uma checagem por igualdade.
        """
        return self == self.__class__.P
