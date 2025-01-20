import pytest

from abc import ABC, abstractmethod

from ..enums import PytestHookEnum

__all__ = 'PytestHook',


class PytestHook(ABC):
    """
    Classe abstrata representando um 'hook' do pytest - quando usado em
    conjunto com a função
    """

    def call(self, hook: PytestHookEnum, *args, **kwargs):
        return {
            PytestHookEnum.CONFIGURE: self.on_configure,
            PytestHookEnum.SESSIONSTART: self.on_sessionstart,
            PytestHookEnum.SESSIONFINISH: self.on_sessionfinish,
            PytestHookEnum.UNCONFIGURE: self.on_unconfigure,
        }[hook](*args, **kwargs)  # noqa

    @abstractmethod
    def on_configure(self, config: pytest.Config):
        pass

    @abstractmethod
    def on_sessionstart(self, session: pytest.Session):
        pass

    @abstractmethod
    def on_sessionfinish(self, session: pytest.Session):
        pass

    @abstractmethod
    def on_unconfigure(self, config: pytest.Config):
        pass
