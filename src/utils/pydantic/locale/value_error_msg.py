from typing import Mapping

__all__ = 'value_error_msg',

# Referência de chaves:
# - limit_value;

value_error_msg: Mapping[str, str] = {
    'value_error.missing': 'Campo obrigatório sem valor informado.',
    'value_error.extra': 'Campos adicionais não são permitidos.',
    'value_error.const': 'O valor informado não é permitido; Valores válidos: '
                         '{permitted}.',
    'value_error.date': 'Formato inválido para data.',
    'value_error.datetime': 'Formato inválido para \'datetime\'.',

    'value_error.any_str.max_length': 'String ultrapassou o tamanho máximo '
                                      'estipulado ({limit_value}).',
    'value_error.number.not_ge': 'O valor informado deverá ser maior ou igual '
                                 'a {limit_value}.',
    'value_error.number.not_gt': 'O valor informado deverá ser maior que '
                                 '{limit_value}.',
    'value_error.number.not_le': 'O valor informado deverá ser menor ou igual '
                                 'a {limit_value}.',
    'value_error.number.not_lt': 'O valor informado deverá ser menor que '
                                 '{limit_value}.',
    'value_error.list.min_items': 'O valor informado deverá conter pelo menos '
                                  '{limit_value} item(s).',
}
"""
Mapeia um tipo de erro do pydantic, que extende ValueError, com sua respectiva
mensagem em pt-br.
"""
