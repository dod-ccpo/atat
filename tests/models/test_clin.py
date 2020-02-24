from atat.models import CLIN
from atat.models.clin import JEDICLINType

from tests.factories import *


def test_is_obligated():
    clin_1 = CLINFactory.create(jedi_clin_type=JEDICLINType.JEDI_CLIN_1)
    assert clin_1.is_obligated()

    clin_2 = CLINFactory.create(jedi_clin_type=JEDICLINType.JEDI_CLIN_2)
    assert not clin_2.is_obligated()

    clin_3 = CLINFactory.create(jedi_clin_type=JEDICLINType.JEDI_CLIN_3)
    assert clin_3.is_obligated()

    clin_4 = CLINFactory.create(jedi_clin_type=JEDICLINType.JEDI_CLIN_4)
    assert not clin_4.is_obligated()


def test_is_completed():
    assert CLINFactory.create().is_completed
