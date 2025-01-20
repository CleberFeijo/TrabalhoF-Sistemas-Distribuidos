from fastapi import Request, status
from fastapi.responses import JSONResponse

from core.settings import env

from ._base import ExceptionHandler

__all__ = 'InternalErrorHandler',


class InternalErrorHandler(ExceptionHandler[Exception]):
    """
    Responsável por tratar os erros não mapeados do sistema, para devolver
    uma resposta mais amistosa para o cliente, e mais detalhada para devs.
    """

    @classmethod
    def handler(cls, request: Request, exc: Exception):
        from common.classes import ExceptionWrapper

        content = {
            'sucesso': False,
            'detalhes': 'Erro interno do sistema.',
        }
        if cls._send_traceback(request):
            ew = ExceptionWrapper(exc).json_serialize()
            content['erro'] = {
                'tipo': ew['exc_type'],
                'mensagem': ew['exc_msg'],
                'traceback': ew['exc_tb'],
            }

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )

    @staticmethod
    def _send_traceback(request: Request) -> bool:
        """Determina se deve exibir os detalhes do erro ocorrido."""
        if not env.is_prod():
            return True
        for header, value in request.headers.items():
            if str(header).lower() == 'send-traceback':
                return True
        return False
