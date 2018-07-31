import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.pe_numbers import PENumbers

from tests.factories import PENumberFactory


@pytest.fixture()
def pe_numbers(db):
    return PENumbers(db)

@pytest.fixture(scope="function")
def new_pe_number(db):
    def make_pe_number(**kwargs):
        pen = PENumberFactory.create(**kwargs)
        db.add(pen)
        db.commit()

        return pen

    return make_pe_number


def test_can_get_pe_number(pe_numbers, new_pe_number):
    new_pen = new_pe_number(number="0701367F", description="Combat Support - Offensive")
    pen = pe_numbers.get(new_pen.number)

    assert pen.number == new_pen.number


def test_nonexistent_pe_number_raises(pe_numbers):
    with pytest.raises(NotFoundError):
        pe_numbers.get("some fake number")

def test_create_many(pe_numbers):
    pen_list = [['123456', 'Land Speeder'], ['7891011', 'Lightsaber']]
    pe_numbers.create_many(pen_list)

    assert pe_numbers.get(pen_list[0][0])
    assert pe_numbers.get(pen_list[1][0])
