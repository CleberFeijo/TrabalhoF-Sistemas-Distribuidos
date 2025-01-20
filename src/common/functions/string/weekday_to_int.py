import re

from typing import Pattern

__all__ = 'weekday_to_int',


_weekday_int_to_pattern: dict[int, Pattern[str]] = {
    0: re.compile(r'SEGUNDA(-FEIRA)?|\bSEG\b', flags=re.I),
    1: re.compile(r'TER[CÇ]A(-FEIRA)?|\bTER\b', flags=re.I),
    2: re.compile(r'QUARTA(-FEIRA)?|\bQUA\b', flags=re.I),
    3: re.compile(r'QUINTA(-FEIRA)?|\bQUI\b', flags=re.I),
    4: re.compile(r'SEXTA(-FEIRA)?|\bSEX\b', flags=re.I),
    5: re.compile(r'S[AÁ]BADO|\bS[AÁ]B\b', flags=re.I),
    6: re.compile(r'DOMINGO|\bDOM\b', flags=re.I),
}
"""
Relaciona o valor número do dia da semana com o padrão de identificação do
mesmo.
"""


def weekday_to_int(weekday: str) -> int:
    """
    Converte um texto contendo o nome do dia da semana em seu valor numérico
    de acordo com o `datetime`.

    - Ex.: "Segunda-feira" possui valor `0`;
    """
    for i, pattern in _weekday_int_to_pattern.items():
        if pattern.search(weekday):
            return i
    raise ValueError(f'"{weekday}" não é um dia da semana válido.')
