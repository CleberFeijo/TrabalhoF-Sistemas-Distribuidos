import logging

from ._base import *

__all__ = 'DefaultFormatter',


class DefaultFormatter(_BaseFormatter):
    """Formatador de logging padrão."""

    __formats__ = {
        logging.DEBUG: MessageFormat(
            suffix='\n* arquivo: %(pathname)s, função: %(funcName)s(), linha %(lineno)d;\n',
        ),
    }

    def default_format(self) -> MessageFormat:
        return MessageFormat(
            prefix='%(asctime)s | %(levelname)s:',
            message='%(message)s',
            suffix='',
        )
