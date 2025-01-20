from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv

from utils.fastapi import OpenAPISchemaFactory

__all__ = 'router',

router = APIRouter(prefix='/exemplo', tags=['Exemplo'])


@cbv(router)
class ExemploCBV:

    @router.get(
        path='/',
        responses=OpenAPISchemaFactory(200),
    )
    def consulta(self):
        pass

    @router.post(
        path='/',
        responses=OpenAPISchemaFactory(200),
    )
    def cadastro(self):
        pass

    @router.patch(
        path='/{exemplo_id}',
        responses=OpenAPISchemaFactory(200),
    )
    def atualizacao(self, exemplo_id):
        pass

    @router.delete(
        path='/{exemplo_id}',
        responses=OpenAPISchemaFactory(200),
    )
    def exclusao(self, exemplo_id):
        pass
