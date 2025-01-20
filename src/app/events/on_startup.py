from core.loggers import Loggers
from core.settings import env

__all__ = 'on_startup',

logger = Loggers()


def on_startup() -> None:
    """Método chamado ao (re)iniciar a aplicação do FastAPI."""

    if env.is_dev():
        _run_flake8()


# =========================== #
# ~~~~| Private Methods |~~~~ #
# =========================== #

def _run_flake8():
    from utils.flake8 import Flake8
    Flake8(logger=logger).check_files()
