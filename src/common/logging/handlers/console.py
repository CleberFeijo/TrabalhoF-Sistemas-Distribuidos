import logging
import sys

__all__ = 'ConsoleHandler',


class ConsoleHandler(logging.StreamHandler):
    """
    Subclasse de `logging.StreamHandler`, responsável por realizar a mesma
    funcionalidade da classe-pai, porém com o stream padrão de `sys.stdout`.
    """
    def __init__(self):
        super().__init__(sys.stdout)
