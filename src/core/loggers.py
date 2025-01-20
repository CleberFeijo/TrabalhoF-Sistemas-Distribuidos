import logging

from logging.handlers import TimedRotatingFileHandler

from common.logging import *
from core.settings import env

__all__ = 'Loggers',


Loggers = LoggerFactory(
    disable_existing_loggers=True,
    formatters={
        'defaultFormatter': FormatterConfig(
            cls=DefaultFormatter,
        ),
        'colorFormatter': FormatterConfig(
            cls=ColorFormatter,
        ),
    },
    handlers={
        'nullHandler': HandlerConfig(
            cls=logging.NullHandler,
        ),
        'consoleHandler': HandlerConfig(
            cls=ConsoleHandler,
            formatter='colorFormatter',
        ),
        'taskExemploFileHandler': HandlerConfig(
            cls=TimedRotatingFileHandler,
            backupCount=7,
            filename='logs/task_exemplo/info.log',
            formatter='defaultFormatter',
            level=LevelEnum.INFO,
            when='midnight',
        ),
    },
    root=LoggerConfig(
        level=LevelEnum.DEBUG if env.is_dev() else LevelEnum.INFO,
        handlers=['consoleHandler'],
        propagate=False,
    ),
    loggers={
        ('gunicorn.access', 'gunicorn.error'): LoggerConfig(
            level=LevelEnum.INFO,
            handlers=['consoleHandler'],
            propagate=False,
        ),
        # Impede a propagação de debugs e output duplicado de logs.
        ('uvicorn', 'flake8'): LoggerConfig(
            propagate=False,
        ),
        'asyncio': LoggerConfig(
            level=LevelEnum.INFO,
        ),
        'taskExemplo': LoggerConfig(
            handlers=['taskExemploFileHandler'],
            level=LevelEnum.DEBUG if env.is_dev() else LevelEnum.INFO,
            propagate=True,
        ),
    },
)
