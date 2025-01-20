import logging

from dataclasses import dataclass
from typing import Optional

__all__ = 'Flake8',


@dataclass
class Flake8:
    """Classe responsável por rodar o flake8 em tempo de execução."""
    logger: Optional[logging.Logger]

    def check_files(self):
        """
        Envelopa o método `flake8.api.legacy.get_style_guide().check_files()`,
        adicionando logs de início e fim do ciclo e silenciando os logs
        de debug nativos do flake8.
        """
        self.log(msg='Checando estilo e qualidade do código com "flake8"...\n')

        from flake8 import LOG
        from flake8.api import legacy as flake8

        LOG.setLevel(logging.CRITICAL)  # Silencia os debugs nativos.
        report = flake8.get_style_guide().check_files()
        LOG.setLevel(logging.INFO)

        self.log(msg=f'Checagem concluída (Problemas encontrados: {report.total_errors}).')

    def log(self, msg: str, level: int = logging.INFO):
        if self.logger:
            self.logger.log(level=level, msg=msg)
