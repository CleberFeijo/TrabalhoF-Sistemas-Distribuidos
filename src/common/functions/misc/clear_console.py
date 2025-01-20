# import os

__all__ = 'clear_console',


def clear_console(newlines: int = 0):
    """
    Limpa o console (windows | linux);

    :param newlines: Número de linhas a serem puladas após a limpeza.
    """
    print('\033[H\033[J', '\n' * newlines)
    # os.system('cls' if os.name == 'nt' else 'clear')
