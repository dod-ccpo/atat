import pytest

from atst.domain.exceptions import NotFoundError
from atst.domain.task_orders import TaskOrders

from tests.factories import TaskOrderFactory


@pytest.fixture()
def task_orders(db):
    return TaskOrders(db)

@pytest.fixture(scope="function")
def new_task_order(db):
    def make_task_order(**kwargs):
        to = TaskOrderFactory.create(**kwargs)
        db.add(to)
        db.commit()

        return to

    return make_task_order


def test_can_get_task_order(task_orders, new_task_order):
    new_to = new_task_order(number="0101969F")
    to = task_orders.get(new_to.number)

    assert to.id == to.id


def test_nonexistent_task_order_raises(task_orders):
    with pytest.raises(NotFoundError):
        task_orders.get("some fake number")
