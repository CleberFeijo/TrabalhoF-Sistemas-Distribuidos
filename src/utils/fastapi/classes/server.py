from abc import ABC, abstractmethod

from common.classes import DefinedDict

__all__ = 'Server', 'ServerOptions',


class ServerOptions(DefinedDict):
    """
    Classe de base para a criação de subclasses contendo os possíveis
    parâmetros de inicialização de um servidor.
    """

    def __init__(self, **kwargs):
        super().__init__({k: v for k, v in kwargs.items() if not k.startswith('_')})


class Server(ABC):
    """
    Classe de base usada para a criação das subclasses usadas para rodar
    a aplicação do FastAPI.
    """

    @abstractmethod
    def run(self):
        pass
