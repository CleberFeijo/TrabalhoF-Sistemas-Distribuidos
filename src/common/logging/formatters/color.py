import logging

from ._base import *
from .default import DefaultFormatter

from ..enums.console_colors import CC

__all__ = 'ColorFormatter',


class ColorFormatter(DefaultFormatter):
    """
    Formatador de logging base, responsável por adicionar cor ao logging de
    acordo com o nível da mensagem.
    """
    __formats__ = {
        logging.DEBUG: MessageFormat(
            suffix=(
                f'\n* arquivo: %(pathname)s, '
                f'função: {CC.YELLOW}%(funcName)s{CC.RESET}(), '
                f'linha {CC.MAGENTA}%(lineno)d{CC.RESET};\n'
            ),
        ),
        logging.WARNING: MessageFormat(
            color=CC.YELLOW,
        ),
        logging.ERROR: MessageFormat(
            color=CC.RED,
        ),
        logging.CRITICAL: MessageFormat(
            color=CC.BG_RED,
        ),
    }
