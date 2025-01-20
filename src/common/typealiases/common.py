from datetime import date, datetime
from types import ModuleType
from typing import TypeAlias

__all__ = 'AnyDateT', 'ModuleT',


AnyDateT: TypeAlias = str | date | datetime
"""Alias para string (em um formato de data válido), date ou datetime."""

ModuleT: TypeAlias = ModuleType
"""Alias para `types.ModuleType`."""
