"""
Módulo contendo os métodos que funcionam como "hooks" dos eventos do FastAPI.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .on_startup import on_startup
from .on_shutdown import on_shutdown

__all__ = 'lifespan',


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Cria a função de `lifespan` usada pelo FastAPI com base nas funções
    "on_startup" e "on_shutdown" definidas neste pacote.
    """
    on_startup()
    yield
    on_shutdown()
