from ._base import ExceptionHandler
from .http_exception import *
from .internal_error import *
from .request_validation_error import *


def it_exception_handlers():
    """Retorna um iterador contendo as subclasses de "ExceptionHandler"."""
    from common.functions import it_subclasses
    yield from it_subclasses(ExceptionHandler, skip_abstract=True)


def map_exception_handlers():
    """
    Retorna uma correlação entre um tipo de exceção e seu respectivo método
    de controle usado pelo fastapi.

    - Usado principalmente com o parâmetro "exception_handlers" ao criar uma
      instância de FastAPI.
    """
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from common.typealiases import Callable, Type, ExceptionT

    _map: dict[Type[ExceptionT], Callable[[Request, ExceptionT], JSONResponse]] = {}
    for e in it_exception_handlers():
        _map.update(e.dict())
    return _map
