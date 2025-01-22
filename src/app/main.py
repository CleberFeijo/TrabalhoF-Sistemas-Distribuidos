from common.enums import EnvEnum
from core.loggers import Loggers
from core.settings import project_settings
from utils.fastapi import App, GunicornOptions, UvicornOptions
from fastapi import Depends, WebSocket, Request
from .routes.v1.deps import get_current_user
from utils.fastapi.models.response import ResponseModelDict
from core.manager import ConnectionManager
from loguru import logger

from .events import *
from .routes.v1 import api

__all__ = 'app',

logger = Loggers()


# Cria a aplicação principal do FastAPI.
app = App(
    use_defaults=True,
    title=project_settings.NOME,
    version=project_settings.VERSAO,
    lifespan=lifespan,
    subapps=(
        App(
            name='api v1',
            path='/v1/api',
            routers=[api],
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

app.app.include_router(api.HistRouter)
app.app.include_router(api.UserRouter)
app.app.include_router(api.AuthRouter)

# Rota padrão de checagem do sistema.
@app.get('/', include_in_schema=False)
async def status():
    return {
        'sucesso': True,
        'detalhes': 'Serviço online.',
        'projeto': project_settings.NOME,
        'versao': project_settings.VERSAO,
    }

manager = ConnectionManager()

@app.app.websocket('/{ws_id}/ws')
async def websocket_endpoint(websocket: WebSocket, ws_id: str, user_name: str):
    try:
        await manager.connect(ws_id, websocket)
        message = f"O usuário {user_name} acabou de entrar no chat!"
        try:
            while message != "----Fim----":
                message = await websocket.receive_text()
                print(f"Essa é a mensagem: {message}")
                await manager.broadcast(
                    id_=ws_id,
                    message=f'{user_name}:\n\t{message}'
                )
        except Exception as e:
            await manager.send_personal_message(
                message=f"error:{e}",
                websocket=websocket
            )
        manager.disconnect(
            id_=ws_id,
            websocket=websocket,
            last_message=message
        )    

        return ResponseModelDict(
            message="Chat finalizado com sucesso!", data={'success': True}
        )
    except Exception as e:
        logger.error(f"Unexpected error in retrieving user profile: {e}")
        raise e

# Inicia o servidor utilizando Uvicorn ou Gunicorn conforme o ambiente.
if __name__ == '__main__':
    app.run_server('app.main:app.app')
