from aenum import StrEnum

__all__ = 'ConsoleColorEnum', 'CC',


class ConsoleColorEnum(StrEnum):
    """
    Subclasse de `aenum.StrEnum`, contendo os códigos responsáveis por
    adicionar cor ao console.
    """
    RESET = '\x1b[0m'
    "Reseta para a cor padrão do console."

    BLACK = '\x1b[30m'
    "Define a cor dos caracteres do console como preta."

    RED = '\x1b[31m'
    "Define a cor dos caracteres do console como vermelha."

    GREEN = '\x1b[32m'
    "Define a cor dos caracteres do console como verde."

    YELLOW = '\x1b[33m'
    "Define a cor dos caracteres do console como amarela."

    BLUE = '\x1b[34m'
    "Define a cor dos caracteres do console como azul."

    MAGENTA = '\x1b[35m'
    "Define a cor dos caracteres do console como magenta."

    CYAN = '\x1b[36m'
    "Define a cor dos caracteres do console como ciano."

    WHITE = '\x1b[37m'
    "Define a cor dos caracteres do console como branca."

    BG_BLACK = '\x1b[40m'
    "Define a cor do background dos caracteres do console como preta."

    BG_RED = '\x1b[41m'
    "Define a cor do background dos caracteres do console como vermelha."

    BG_GREEN = '\x1b[42m'
    "Define a cor do background dos caracteres do console como verde."

    BG_YELLOW = '\x1b[43m'
    "Define a cor do background dos caracteres do console como amarela."

    BG_BLUE = '\x1b[44m'
    "Define a cor do background dos caracteres do console como azul."

    BG_MAGENTA = '\x1b[45m'
    "Define a cor do background dos caracteres do console como magenta."

    BG_CYAN = '\x1b[46m'
    "Define a cor do background dos caracteres do console como ciano."

    BG_WHITE = '\x1b[47m'
    "Define a cor do background dos caracteres do console como branca."


CC = ConsoleColorEnum
"Alias para `ConsoleColorEnum`."
