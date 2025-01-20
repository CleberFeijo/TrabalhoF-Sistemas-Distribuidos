from fastapi import FastAPI

from ..classes import Server, ServerOptions
from ..servers import (
    GunicornOptions,
    GunicornServer,
    UvicornOptions,
    UvicornServer,
)

__all__ = 'run_server',


def run_server(
        app: FastAPI,
        app_path: str,
        options: ServerOptions,
) -> Server:
    """
    Cria a instância da respectiva subclasse de `utils.fastapi.classes.Server`
    de acordo com o tipo das opções recebidas e aciona o método `.run`.

    :param app: Instância de FastAPI que será vinculada à aplicação;
    :param app_path: String no formato "módulo:instância" da aplicação FastAPI;
    :param options: Objeto contendo as opções usadas para criar a instância do
        servidor.
    """
    if isinstance(options, UvicornOptions):
        if options.use_app_path:
            app = app_path
        UvicornServer(app=app, options=options).run()
    elif isinstance(options, GunicornOptions):
        GunicornServer(app=app, options=options).run()
    else:
        raise TypeError(options)
