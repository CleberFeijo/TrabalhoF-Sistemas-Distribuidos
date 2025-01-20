from typing import Mapping

__all__ = 'type_error_msg',

# Referência de chaves:
# - enum_values;

type_error_msg: Mapping[str, str] = {
    'type_error.integer': 'Valor informado não é um inteiro válido.',
    'type_error.list': 'Valor informado não é uma lista válida.',
    'type_error.bool': 'Valor informado não é um booleano válido.',
    'type_error.none.not_allowed': 'Valor nulo não é permitido.',
    'type_error.enum': 'Valor informado não é válido - as opções válidas são: '
                       '{enum_values}.'
}
"""
Mapeia um tipo de erro do pydantic, que extende TypeError, com sua respectiva
mensagem em pt-br.
"""
