from flake8.formatting.base import BaseFormatter, Violation

from common.logging import CC

__all__ = 'ColorFormatter',


class ColorFormatter(BaseFormatter):
    """
    Subclasse de `flake8.formatting.base.BaseFormatter` responsável por alterar
    a formatação da(s) mensagem(ns) de violação de estilo/qualidade do código.
    """

    def format(self, error: Violation):
        code = f'{self._color_for_code(error.code)}[{error.code}]{CC.RESET}'
        line = f'{CC.MAGENTA}{error.line_number}{CC.RESET}'
        filename = error.filename
        text = error.text

        return f'* {code}: {text};\n* arquivo: {filename}, linha {line};\n'

    @staticmethod
    def _color_for_code(code: str) -> CC:
        if code.startswith('W'):
            return CC.YELLOW
        return CC.RED
