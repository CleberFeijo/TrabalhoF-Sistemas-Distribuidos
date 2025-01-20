from fastapi import FastAPI
from gunicorn.app.base import BaseApplication
from typing import Union

from .options import GunicornOptions

from ...classes import Server

__all__ = 'GunicornServer',


class GunicornServer(BaseApplication, Server):
    """
    Classe usada para rodar um servidor de Gunicorn programaticamente.
    """

    def __init__(
            self,
            app: FastAPI,
            options: Union[dict, GunicornOptions, None] = None,
    ):
        def _adjust_options(o):
            if isinstance(o, GunicornOptions):
                return o
            elif isinstance(o, dict):
                return GunicornOptions(**o)
            elif o is None:
                return GunicornOptions()
            raise ValueError(o)

        self.options = _adjust_options(options)
        self.app = app
        super().__init__()

    def load_config(self):
        for key, value in (self.options or {}).items():
            self.cfg.set(key, value)

    def load(self):
        return self.app
