import pytest


def pytest_configure(config: pytest.Config):
    pass


def pytest_sessionstart(session: pytest.Session):
    pass


def pytest_sessionfinish(session: pytest.Session):
    pass


def pytest_unconfigure(config: pytest.Config):
    pass
