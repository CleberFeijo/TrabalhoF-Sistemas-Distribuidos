from bson import ObjectId
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, IntEnum
from pytest import fixture
from pytest_unordered import unordered


# ==================== #
# ~~~~| Fixtures |~~~~ #
# ==================== #

@fixture
def json_encoder():
    from common.serializers import JSONEncoder
    return JSONEncoder()


@fixture
def temp_dataclass():

    @dataclass
    class TempDataClass:
        a: int
        b: bool
        c: str = 'teste'

    return TempDataClass


@fixture
def temp_enum():
    class TempEnum(Enum):
        a = 'A'
        b = 'B'

    return TempEnum


@fixture
def temp_intenum():
    class TempIntEnum(IntEnum):
        a = 1
        b = 2
    return TempIntEnum


# ================= #
# ~~~~| Tests |~~~~ #
# ================= #

def test_encode_datetime(json_encoder):
    encoded = json_encoder.dump(datetime(2023, 1, 1, 15, 30))
    assert encoded == '2023-01-01 15:30:00'


def test_encode_date(json_encoder):
    encoded = json_encoder.dump(date(2023, 2, 2))
    assert encoded == '2023-02-02'


def test_encode_oid(json_encoder):
    encoded = json_encoder.dump(ObjectId('63eac3d8deb6d0134fc606e8'))
    assert encoded == '63eac3d8deb6d0134fc606e8'


def test_encode_enum(json_encoder, temp_enum, temp_intenum):
    encoded = json_encoder.dump(temp_enum.a)
    assert encoded == 'A'
    encoded = json_encoder.dump(temp_intenum.b)
    assert encoded == 2


def test_encode_type(json_encoder, temp_dataclass):
    encoded = json_encoder.dump(temp_dataclass)
    assert encoded == 'TempDataClass'


def test_encode_dataclass(json_encoder, temp_dataclass):
    encoded = json_encoder.dump(temp_dataclass(a=1, b=False))  # noqa
    assert encoded == {'a': 1, 'b': False, 'c': 'teste'}


def test_encode_nested(json_encoder, temp_dataclass, temp_enum, temp_intenum):
    encoded = json_encoder.dump({
        'datetime': {
            datetime(2022, 12, 31, 12, 15),
            date(2022, 1, 1),
        },
        'enum': deque([
            temp_enum.b,
            temp_intenum.a,
        ]),
        'oid': ObjectId('63eb7f07c794cfcd9f37cc9d'),
        'type': temp_dataclass,
    })
    assert encoded == {
        'datetime': unordered('2022-12-31 12:15:00', '2022-01-01'),
        'enum': unordered('B', 1),
        'oid': '63eb7f07c794cfcd9f37cc9d',
        'type': 'TempDataClass',
    }
