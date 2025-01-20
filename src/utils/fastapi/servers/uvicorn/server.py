import uvicorn

from fastapi import FastAPI
from typing import Union

from .options import UvicornOptions

from ...classes import Server

__all__ = 'UvicornServer',


class UvicornServer(Server):
    """Classe usada para rodar um servidor de Uvicorn programaticamente."""

    def __init__(
            self,
            app: FastAPI,
            options: Union[dict, UvicornOptions, None] = None,
    ):
        def _adjust_options(o):
            if isinstance(o, UvicornOptions):
                return o
            elif isinstance(o, dict):
                return UvicornOptions(**o)
            elif o is None:
                return UvicornOptions()
            raise ValueError(o)

        self.options = _adjust_options(options)
        self.app = app
        super().__init__()

    # noinspection PydanticTypeChecker
    def run(self):
        uvicorn.run(app=self.app, **self.options)
