"""Erros de domínio e tratadores que padronizam as respostas de erro da API.

Formato de toda resposta de erro:
    {"error": {"code": "not_found", "message": "...", "details": [...]}}
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("hist.errors")


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"
    message = "Requisição inválida."

    def __init__(self, message: str | None = None, *, code: str | None = None, details=None):
        self.message = message or self.message
        self.code = code or self.code
        self.details = details
        super().__init__(self.message)


class NotFound(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    message = "Recurso não encontrado."


class Unauthorized(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    message = "Credenciais inválidas ou ausentes."


class Forbidden(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"
    message = "Você não tem permissão para executar esta ação."


class Conflict(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    message = "Conflito com o estado atual do recurso."


def _body(code: str, message: str, details=None) -> dict:
    error = {"code": code, "message": message}
    if details:
        error["details"] = details
    return {"error": error}


async def _app_error(_: Request, exc: AppError):
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return JSONResponse(_body(exc.code, exc.message, exc.details), status_code=exc.status_code, headers=headers)


async def _validation_error(_: Request, exc: RequestValidationError):
    details = [
        {
            "field": ".".join(str(p) for p in err.get("loc", []) if p != "body"),
            "message": err.get("msg"),
            "type": err.get("type"),
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        _body("validation_error", "Dados da requisição inválidos.", details),
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def _http_error(_: Request, exc: StarletteHTTPException):
    codes = {401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}
    return JSONResponse(
        _body(codes.get(exc.status_code, "http_error"), str(exc.detail)),
        status_code=exc.status_code,
        headers=getattr(exc, "headers", None),
    )


async def _unhandled_error(request: Request, exc: Exception):
    # Detalhes ficam apenas no log do servidor, nunca na resposta.
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        _body("internal_error", "Erro interno do servidor."),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unhandled_error)
