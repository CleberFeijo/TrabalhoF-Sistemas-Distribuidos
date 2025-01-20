from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id as default_generate_unique_id
from uuid import uuid4

__all__ = 'generate_unique_id',


def generate_unique_id(route: APIRoute) -> str:
    """
    Cria um id único para cada rota utilizando o gerador de id padrão do
    fastapi.

    :param route:
    :return:
    """
    return f'{uuid4()}_{route.endpoint.__qualname__}_{default_generate_unique_id(route)}'
