from datetime import datetime, time

__all__ = 'clear_time',


def clear_time(d: datetime) -> datetime:
    """
    Responsável por criar um novo datetime com horário zerado.

    :param d: datetime de base.
    :return: datetime com horário zerado.
    """
    return datetime.combine(d.date(), time.min)
