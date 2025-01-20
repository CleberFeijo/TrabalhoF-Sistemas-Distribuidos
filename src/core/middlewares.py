import time

from fastapi import Request

__all__ = (
    "request_handler",
    "add_process_time_header",
    "add_access_to_headers"
)


async def request_handler(request: Request, call_next):
    """
    Middleware utilizado para processar cada requisição no FastAPI,
    para prover tratamento de erros (converte exceções em respostas).
    """

    try:
        return await call_next(request)
    except Exception as e:
        raise e


async def add_process_time_header(request: Request, call_next):
    """
    Middleware simples para mensurar o tempo entre a chegada de uma
    request e a saída de uma resposta.
    """

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def add_access_to_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["access-control-allow-origin"] = "*"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
