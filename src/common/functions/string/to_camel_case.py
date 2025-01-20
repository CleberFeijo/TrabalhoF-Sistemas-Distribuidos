__all__ = 'to_camel_case',


def to_camel_case(s: str) -> str:
    """
    Converte uma string para "camelCase".

    A conversão pode ser feita para strings nos seguintes formatos:

    - PascalCase -> pascalCase;
    - snake_case -> snakeCase;
    - SCREAMING_SNAKE_CASE -> screamingSnakeCase;
    - kebab-case -> kebabCase;
    - UPPERCASE -> uppercase;
    - lowercase -> lowercase;
    - Titlecase -> titlecase;

    :param s: String a ser convertida;
    :return: String convertida para "camelCase".
    """
    new_str = ''
    "Versão tratada da string que será retornada."

    first_letter = True
    upper = False

    # Se a string inteira estiver em upper case, transforma para "lowercased".
    if s.isupper():
        s = s.lower()

    # Itera sobre os caracteres da string.
    for char in s.strip():

        # Se o caractere não for alfa-numérico, determina que o próx. deverá
        # ser "uppercased".
        if not char.isalnum():
            upper = True
            continue

        # Se for a primeira letra válida, seta como "lowercased".
        if first_letter:
            char = char.lower()
            first_letter = False
            upper = False

        # Caso seja precedido por um símbolo ou espaço, converte para "uppercased".
        elif upper:
            char = char.upper()
            upper = False

        new_str += char

    return new_str
