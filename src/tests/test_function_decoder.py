from bson import ObjectId
from datetime import date
from pydantic import ValidationError
from typing import Optional, Sequence, Union, TypeVar

from utils.pydantic import decode_parameters


def test_function_without_annotation():
    @decode_parameters
    def f(a, b, c):
        return a, b, c

    assert f(1, 2, 3) == (1, 2, 3)


def test_function_with_basic_annotation():
    @decode_parameters
    def f(a: int, b: bool, c: str):
        return a, b, c

    assert f('1', 0, 123) == (1, False, '123')


def test_function_with_nested_annotation():
    @decode_parameters
    def f(a: dict[str, list[date]]):
        return a

    decoded = f({
        'a': ['2022-01-01'],
        'b': set(),
        'c': ('08/08/1995', '2023-01-01 10:50:00'),
    })
    expected = {
        'a': [date(2022, 1, 1)],
        'b': [],
        'c': [date(1995, 8, 8), date(2023, 1, 1)],
    }
    assert decoded == expected


def teste_decorator_with_specific_arguments():
    @decode_parameters('a')
    def f(a: date, b: date):
        return a, b
    assert f('1970-01-01', b='2023-02-15') == (date(1970, 1, 1), '2023-02-15')


def test_default_value():
    @decode_parameters
    def f(a: date = '1999-12-31'):
        return a

    # Não realiza o decode para valores padrão!
    assert f() == '1999-12-31'
    assert f('1999-12-31') == date(1999, 12, 31)


def test_args_kwargs():
    @decode_parameters
    def f(a: ObjectId, *args, **kwargs):
        return a, args, kwargs

    decoded = f(
        '63bc760a7165ff4a02f63433',
        '63bc9fbf7165ff4cc8f63433',
        b='63bd6db37165ff54c5f63433',
    )
    expected = (
        ObjectId('63bc760a7165ff4a02f63433'),
        ('63bc9fbf7165ff4cc8f63433',),
        {'b': '63bd6db37165ff54c5f63433'},
    )
    assert decoded == expected


def test_with_union():

    # Quando o tipo informado não consta no tipo esperado, executa a conversão.
    @decode_parameters
    def f(a: Union[int, date]):
        return a
    assert f('2011-11-11') == date(2011, 11, 11)

    # Quando o tipo informado consta no tipo esperado, não executa a conversão.
    @decode_parameters
    def f(a: Union[str, date]):
        return a
    assert f('2011-11-11') == '2011-11-11'

    # Ordem invertida não importa!
    @decode_parameters
    def f(a: Union[date, str]):
        return a
    assert f('2011-11-11') == '2011-11-11'

    # Passar o parâmetro já convertido não dá problema.
    @decode_parameters
    def f(a: Union[date, str]):
        return a
    assert f(date(2011, 11, 11)) == date(2011, 11, 11)

    # Teste com a sintaxe com pipe.
    @decode_parameters
    def f(a: int | date):
        return a
    assert f('2011-11-11') == date(2011, 11, 11)


def test_optional():
    @decode_parameters
    def f(a: Optional[list]):
        return a
    assert f(None) is None


def test_with_class():
    class TempClass:

        @decode_parameters
        def instance_method(self, a: date):
            return a

        @classmethod
        @decode_parameters  # Deve ficar abaixo do @classmethod
        def class_method(cls, b: ObjectId):
            return b

    decoded = TempClass().instance_method('2000-01-01')
    expected = date(2000, 1, 1)
    assert decoded == expected

    decoded = TempClass().class_method('63ed27d8f8a3ca651c7bbcf3')
    expected = ObjectId('63ed27d8f8a3ca651c7bbcf3')
    assert decoded == expected


def test_typevar():
    T = TypeVar('T')  # noqa

    @decode_parameters
    def f(a: T) -> T:
        return a

    assert f(1) == 1


def test_generic():
    @decode_parameters
    def f(a: Sequence):
        return a

    assert f([1, 2, 3]) == [1, 2, 3]
    assert f(('a', 'b')) == ('a', 'b')

    try:
        f({True})
        raise AssertionError('Não realizou a validação de sequência!')
    except ValidationError:
        pass

    # pydantic v2 corrigiu o erro de string não ser sequência!
    assert f('a') == 'a'
