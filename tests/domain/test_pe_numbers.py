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
    new_pen = new_pe_number(number="0101969F", description="Combat Support - Offensive")
    pen = pe_numbers.get(new_pen.number)

    assert pen.number == new_pen.number


def test_nonexistent_pe_number_raises(pe_numbers):
    with pytest.raises(NotFoundError):
        pe_numbers.get("some fake number")
