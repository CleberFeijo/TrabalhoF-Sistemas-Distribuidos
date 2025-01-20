import re

from typing import Pattern

__all__ = 'month_to_int',


_month_int_to_pattern: dict[int, Pattern[str]] = {
    1: re.compile(r'JANEIRO|\bJAN\b', flags=re.I),
    2: re.compile(r'FEVEREIRO|\bFEV\b', flags=re.I),
    3: re.compile(r'MAR[CÇ]O|\bMAR\b', flags=re.I),
    4: re.compile(r'ABRIL|\bABR\b', flags=re.I),
    5: re.compile(r'MAIO|\bMAI\b', flags=re.I),
    6: re.compile(r'JUNHO|\bJUN\b', flags=re.I),
    7: re.compile(r'JULHO|\bJUL\b', flags=re.I),
    8: re.compile(r'AGOSTO|\bAGO\b', flags=re.I),
    9: re.compile(r'SETEMBRO|\bSET\b', flags=re.I),
    10: re.compile(r'OUTUBRO|\bOUT\b', flags=re.I),
    11: re.compile(r'NOVEMBRO|\bNOV\b', flags=re.I),
    12: re.compile(r'DEZEMBRO|\bDEZ\b', flags=re.I),
}
"""Relaciona o valor número do mês com o padrão de identificação do mesmo."""


def month_to_int(month: str) -> int:
    """
    Converte um texto contendo o nome do mês em seu valor numérico de acordo
    com o `datetime`.
    """
    for i, pattern in _month_int_to_pattern.items():
        if pattern.search(month):
            return i
    raise ValueError(f'"{month}" não é um mês válido.')
