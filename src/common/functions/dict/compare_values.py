from typing import Optional

__all__ = 'compare_values',


def compare_values(dict_a: dict, dict_b: dict) -> Optional[dict]:
    """
    Compara dois dicts e retorna um dict com os campos diferentes.

    :param dict_a: dict a ser comparado
    :param dict_b: dict a ser comparado
    :return: dict com as diferenças de valores
    """
    dictdiff = {}
    for ka, va in dict_a.items():
        for kb, vb in dict_b.items():
            if ka != kb:
                continue
            if va == vb:
                break
            dictdiff[ka] = vb

    return dictdiff or None
