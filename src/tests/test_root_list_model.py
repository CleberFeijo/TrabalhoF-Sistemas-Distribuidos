from pytest import fixture
from pytest_unordered import unordered

from utils.pydantic import RootListModel


# ==================== #
# ~~~~| Fixtures |~~~~ #
# ==================== #

@fixture
def model_class():
    class IntListModel(RootListModel[int]):
        ...
    return IntListModel


# ================= #
# ~~~~| Tests |~~~~ #
# ================= #

def test_create_instance_by_args(model_class):
    model = model_class('1', 2, 3.0)
    assert model == [1, 2, 3]
    assert model.model_dump_json() == '[1,2,3]'


def test_create_instance_by_keyword_arg(model_class):
    model = model_class(root=['2'])
    assert model == [2]
    assert model.model_dump_json() == '[2]'


def test_create_instance_by_single_arg(model_class):
    model = model_class([4, 5])
    assert model == [4, 5]


def test_create_instance_while_type_converting(model_class):
    model = model_class({0, 8, 9, 8, 0})
    assert model == unordered(0, 8, 9)
