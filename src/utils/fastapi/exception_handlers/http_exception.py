from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ._base import ExceptionHandler

__all__ = 'HTTPExcHandler', 'StarletteHTTPExcHandler',


class HTTPExcHandler(ExceptionHandler[HTTPException]):

    @classmethod
    def handler(cls, request, exc: HTTPException):
        from utils.fastapi.factories import OpenAPISchema

        try:
            detalhes = OpenAPISchema(exc.status_code).get('description')
        except ValueError:
            detalhes = exc.detail

        return JSONResponse(
            status_code=exc.status_code,
            content={'sucesso': False, 'detalhes': detalhes},
        )


class StarletteHTTPExcHandler(HTTPExcHandler):
    """
    Mesma tratativa que o "HTTPExcHandler", mas lida com a exceção original do
    Starlette, que pode ocorrer em alguns casos (404 por ex.).
    """
    __exc_type__ = StarletteHTTPException
