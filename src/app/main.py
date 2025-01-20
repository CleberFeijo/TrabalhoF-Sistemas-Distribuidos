from common.enums import EnvEnum
from core.loggers import Loggers
from core.middlewares import (
    add_process_time_header,
    request_handler,
    add_access_to_headers,
)
from core.settings import project_settings
from utils.fastapi import App, GunicornOptions, UvicornOptions
from fastapi.middleware.cors import CORSMiddleware

from .events import *
from .routes.v1 import api

__all__ = 'app',

logger = Loggers()


# Cria a aplicação principal do FastAPI.
app = App(
    use_defaults=True,
    title=project_settings.NOME,
    version=project_settings.VERSAO,
    docs_url=None,  # Somente as sub aplicações têm acesso ao swagger.
    redoc_url=None,  # Somente as sub aplicações têm acesso ao redoc.
    lifespan=lifespan,
    subapps=(
        App(
            name='api v1',
            path='/v1/api',
            routers=api,
            title=f'{project_settings.NOME} - API',
        ),
    ),
    server_options={
        EnvEnum.DEVELOP: UvicornOptions(
            use_defaults=True,
        ),
        EnvEnum.HOMOLOG: GunicornOptions(
            use_defaults=True,
        ),
        EnvEnum.PRODUCTION: GunicornOptions(
            use_defaults=True,
        ),
    },
)


# Rota padrão de checagem do sistema.
@app.get('/', include_in_schema=False)
async def status():
    return {
        'sucesso': True,
        'detalhes': 'Serviço online.',
        'projeto': project_settings.NOME,
        'versao': project_settings.VERSAO,
    }


# Inicia o servidor utilizando Uvicorn ou Gunicorn conforme o ambiente.
if __name__ == '__main__':
    app.run_server('app.main:app.app')
