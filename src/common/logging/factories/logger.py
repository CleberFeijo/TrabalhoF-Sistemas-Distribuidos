import logging

from logging.config import dictConfig
from typing import Any, Optional, Union

from common.classes import UNDEFINED

from ..config import *

__all__ = 'LoggerFactory',


class LoggerFactory:
    """
    Classe auxiliar responsável por configurar os loggers do sistema e prover
    acesso aos mesmos.

    Recomenda-se criar um *singleton* desta classe contendo as configurações
    dos loggers e os acessar a partir desta ao invés de utilizar a função
    `"logging.getLogger()"`, para garantir que o logging esteja sempre com as
    configurações adequadas.
    """

    # ========================= #
    # ~~~~| Magic Methods |~~~~ #
    # ========================= #

    def __init__(
            self,
            config: dict[str, Any] = UNDEFINED,
            /,
            *,
            formatters: Optional[dict[Union[str, tuple[str, ...]], FormatterConfig]] = UNDEFINED,
            handlers: Optional[dict[Union[str, tuple[str, ...]], HandlerConfig]] = UNDEFINED,
            loggers: Optional[dict[Union[str, tuple[str, ...]], LoggerConfig]] = UNDEFINED,
            root: Optional[LoggerConfig] = UNDEFINED,
            incremental: Optional[bool] = UNDEFINED,
            disable_existing_loggers: Optional[bool] = UNDEFINED,
    ):
        _dict_config = config or {}

        self._config_formatters(_dict_config, formatters)
        self._config_handlers(_dict_config, handlers)
        self._config_loggers(_dict_config, loggers)
        self._config_root(_dict_config, root)
        self._config_incremental(_dict_config, incremental)
        self._config_disable_existing_loggers(_dict_config, disable_existing_loggers)

        self.config = {
            'version': 1,  # Campo obrigatório para implementação retroativa do python.
            **_dict_config
        }
        dictConfig(self.config)

    def __call__(self, name: Optional[str] = None) -> logging.Logger:
        logger = logging.getLogger(name)
        if name and not hasattr(self, name):
            setattr(self, name, logger)
        return logger

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    @staticmethod
    def _config(
            conf: dict,
            key: str,
            value: Any,
            expected_types: Union[type, tuple[type, ...]] = None,
    ):
        if value != UNDEFINED:
            conf[key] = value
        if expected_types and not isinstance(conf.get(key), expected_types):
            conf.pop(key, None)

    @staticmethod
    def _spread_names(conf: Optional[dict[Union[str, tuple[str, ...]], Any]]):
        if not isinstance(conf, dict):
            return

        tuples = tuple(t for t in conf.keys() if isinstance(t, tuple))

        for name_as_tuple in tuples:
            value = conf.pop(name_as_tuple)
            conf.update({n: value for n in name_as_tuple})

    @classmethod
    def _config_formatters(
            cls,
            conf: dict,
            formatters: Optional[dict[Union[str, tuple[str, ...]], FormatterConfig]],
    ):
        cls._config(conf, 'formatters', formatters, dict)

        for name, formatter in conf.get('formatters', {}).items():
            if isinstance(formatter, FormatterConfig):
                continue
            conf['formatters'][name] = FormatterConfig(**formatter)

        cls._spread_names(conf['formatters'])

    @classmethod
    def _config_handlers(
            cls,
            conf: dict,
            handlers: Optional[dict[Union[str, tuple[str, ...]], HandlerConfig]],
    ):
        cls._config(conf, 'handlers', handlers, dict)

        for name, handler in conf.get('handlers', {}).items():
            if isinstance(handler, HandlerConfig):
                continue
            conf['handlers'][name] = HandlerConfig(**handler)

        cls._spread_names(conf['handlers'])

    @classmethod
    def _config_loggers(
            cls,
            conf: dict,
            loggers: Optional[dict[Union[str, tuple[str, ...]], LoggerConfig]],
    ):
        cls._config(conf, 'loggers', loggers, dict)

        for name, logger in conf.get('loggers', {}).items():
            if isinstance(logger, LoggerConfig):
                continue
            conf['loggers'][name] = LoggerConfig(**logger)

        cls._spread_names(conf['loggers'])

    @classmethod
    def _config_root(cls, conf: dict, root: Optional[LoggerConfig]):
        cls._config(conf, 'root', root, dict)

        if conf.get('root') and not isinstance(conf['root'], LoggerConfig):
            conf['root'] = LoggerConfig(**conf[root])

    @classmethod
    def _config_incremental(cls, conf: dict, incremental: Optional[bool]):
        cls._config(conf, 'incremental', incremental, dict)

    @classmethod
    def _config_disable_existing_loggers(
            cls,
            conf: dict,
            disable_existing_loggers: Optional[bool],
    ):
        cls._config(conf, 'disable_existing_loggers', disable_existing_loggers, dict)
