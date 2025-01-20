from common.constants import (
    MONTH_TO_SECONDS,
    DAY_TO_SECONDS,
    HOUR_TO_SECONDS,
    MINUTE_TO_SECONDS,
)

__all__ = 'time_to_seconds',


def time_to_seconds(
        *,
        years: float = 0,
        months: float = 0,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
) -> float:
    """
    Função auxiliar para converter determinado período de tempo em segundos.

    :param years: Quantidade de anos (contados como 365 dias);
    :param months: Quantidade de meses (contados como meses comerciais);
    :param days: Quantidade de dias;
    :param hours: Quantidade de horas;
    :param minutes: Quantidade de minutos;
    :param seconds: Quantidade de segundos de base (para não precisar fazer
        somas);
    """
    return sum([
        years * 365 * DAY_TO_SECONDS,
        months * MONTH_TO_SECONDS,
        days * DAY_TO_SECONDS,
        hours * HOUR_TO_SECONDS,
        minutes * MINUTE_TO_SECONDS,
        seconds,
    ])
