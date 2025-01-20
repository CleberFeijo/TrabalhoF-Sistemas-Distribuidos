from celery.exceptions import SoftTimeLimitExceeded
from typing import Iterator, Type

__all__ = 'get_auto_retry_exceptions',


def get_auto_retry_exceptions() -> Iterator[Type[Exception]]:
    """
    Generator responsável por retornar as exceções que uma tarefa celery
    entende que deva permitir que a tarefa possa ser executada novamente.
    """
    yield SoftTimeLimitExceeded

    # Caso esteja com a lib `pymongo`, incrementa os erros da lista.
    try:
        # noinspection PyUnresolvedReferences
        import pymongo.errors
        yield pymongo.errors.ConnectionFailure
    except ImportError:
        pass

    # Caso esteja com a lib `requests`, incrementa os erros da lista.
    try:
        # noinspection PyUnresolvedReferences
        import requests.exceptions
        yield requests.exceptions.ConnectionError
        yield requests.exceptions.Timeout
    except ImportError:
        pass

    # Caso esteja com a lib `httpx`, incrementa os erros da lista.
    try:
        import httpx
        yield httpx.NetworkError
        yield httpx.TimeoutException
    except ImportError:
        pass
