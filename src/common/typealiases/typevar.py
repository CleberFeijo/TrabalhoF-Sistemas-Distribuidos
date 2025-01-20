from typing import TypeVar

__all__ = 'T', 'ExceptionT',


T = TypeVar('T')
"TypeVar genérico, pode ser qualquer tipo."

ExceptionT = TypeVar('ExceptionT', bound=Exception)
"""
TypeVar genérico vinculado à 'Exception', indicando que deve ser uma instância
de uma exceção.
"""
