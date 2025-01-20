from utils.pydantic import RootModel


# ================= #
# ~~~~| Tests |~~~~ #
# ================= #

def test_declare_with_generic():
    class IntModel(RootModel[int]):
        pass

    model = IntModel('1')
    assert model.root == 1
    assert model.model_dump_json() == '1'

    model = IntModel(root='2')
    assert model.root == 2
    assert model.model_dump_json() == '2'


def test_explicity_declaration():
    class StrModel(RootModel):
        root: str

    model = StrModel('asd')
    assert model.root == 'asd'
    assert model.model_dump_json() == '"asd"'

    model = StrModel(root=123)
    assert model.root == '123'
    assert model.model_dump_json() == '"123"'


def test_ovewrite_declaration():
    class FloatModel(RootModel[int]):
        root: float

    model = FloatModel(1.5)
    assert model.root == 1.5
    assert model.model_dump_json() == '1.5'
