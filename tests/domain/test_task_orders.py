from decimal import Decimal

import pendulum
import pytest

from atat.domain.exceptions import AlreadyExistsError
from atat.domain.task_orders import TaskOrders
from atat.models import Attachment, PortfolioStates
from atat.models.task_order import SORT_ORDERING, Status, TaskOrder
from tests.factories import CLINFactory, PortfolioFactory, TaskOrderFactory


@pytest.fixture
def new_task_order():
    return TaskOrderFactory.create(create_clins=[{}])


@pytest.fixture
def updated_task_order():
    return TaskOrderFactory.create(
        create_clins=[{"last_sent_at": pendulum.date(2020, 2, 1)}],
        pdf_last_sent_at=pendulum.date(2020, 1, 1),
    )


@pytest.fixture
def sent_task_order():
    return TaskOrderFactory.create(
        create_clins=[{"last_sent_at": pendulum.date(2020, 1, 1)}],
        pdf_last_sent_at=pendulum.date(2020, 1, 1),
    )


def test_create_adds_clins():
    portfolio = PortfolioFactory.create()
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.create(
        portfolio_id=portfolio.id,
        number="0123456789",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert len(task_order.clins) == 2


def test_update_adds_clins():
    task_order = TaskOrderFactory.create(number="1231231234")
    to_number = task_order.number
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.create(
        portfolio_id=task_order.portfolio_id,
        number="0000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert task_order.number != to_number
    assert len(task_order.clins) == 2


def test_update_does_not_duplicate_clins():
    task_order = TaskOrderFactory.create(
        number="3453453456123", create_clins=[{"number": "123"}, {"number": "456"}]
    )
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "123",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "111",
            "start_date": pendulum.date(2020, 1, 1),
            "end_date": pendulum.date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
    ]
    task_order = TaskOrders.update(
        task_order_id=task_order.id,
        number="0000000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert len(task_order.clins) == 2
    for clin in task_order.clins:
        assert clin.number != "456"


def test_delete_task_order_with_clins(session):
    task_order = TaskOrderFactory.create(
        create_clins=[{"number": 1}, {"number": 2}, {"number": 3}]
    )
    TaskOrders.delete(task_order.id)

    assert not session.query(
        session.query(TaskOrder).filter_by(id=task_order.id).exists()
    ).scalar()


def test_task_order_sort_by_status():
    today = pendulum.today(tz="UTC")
    yesterday = today.subtract(days=1)
    future = today.add(days=100)

    initial_to_list = [
        # Draft
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        # Active
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        # Upcoming
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
        # Expired
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        # Unsigned
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
    ]

    sorted_by_status = TaskOrders.sort_by_status(initial_to_list)
    assert len(sorted_by_status["Draft"]) == 4
    assert len(sorted_by_status["Active"]) == 1
    assert len(sorted_by_status["Upcoming"]) == 1
    assert len(sorted_by_status["Expired"]) == 2
    with pytest.raises(KeyError):
        sorted_by_status["Unsigned"]
    assert list(sorted_by_status.keys()) == [status.value for status in SORT_ORDERING]


def test_create_enforces_unique_number():
    portfolio = PortfolioFactory.create()
    number = "1234567890123"
    assert TaskOrders.create(portfolio.id, number, [], None)
    with pytest.raises(AlreadyExistsError):
        TaskOrders.create(portfolio.id, number, [], None)


def test_update_enforces_unique_number():
    task_order = TaskOrderFactory.create()
    dupe_task_order = TaskOrderFactory.create()
    with pytest.raises(AlreadyExistsError):
        TaskOrders.update(dupe_task_order.id, task_order.number, [], None)


def test_allows_alphanumeric_number():
    portfolio = PortfolioFactory.create()
    valid_to_numbers = ["1234567890123", "ABC1234567890"]

    for number in valid_to_numbers:
        assert TaskOrders.create(portfolio.id, number, [], None)


def test_get_for_send_task_order_files(
    new_task_order, updated_task_order, sent_task_order
):
    updated_and_new_task_orders = TaskOrders.get_for_send_task_order_files()
    assert len(updated_and_new_task_orders) == 2
    assert sent_task_order not in updated_and_new_task_orders
    assert updated_task_order in updated_and_new_task_orders
    assert new_task_order in updated_and_new_task_orders


class Test_get_clins_for_create_billing_instructions:
    @pytest.fixture
    def provisioned_task_order(self):
        return TaskOrderFactory.create(
            portfolio=PortfolioFactory.create(state=PortfolioStates.COMPLETED.name),
            create_clins=[{}],
        )

    @pytest.fixture
    def sent_task_order(self):
        return TaskOrderFactory.create(
            create_clins=[{"last_sent_at": pendulum.date(2020, 1, 1)}],
        )

    def test_sent_task_order(self, sent_task_order):
        new_clins = TaskOrders.get_clins_for_create_billing_instructions()
        assert len(new_clins) == 0

    def test_portfolio_is_completed(self, provisioned_task_order):
        new_clins = TaskOrders.get_clins_for_create_billing_instructions()
        assert provisioned_task_order.clins == new_clins

    def test_portfolio_is_not_completed(self):
        task_order = TaskOrderFactory.create(
            portfolio=PortfolioFactory.create(state=PortfolioStates.UNSTARTED.name),
            create_clins=[{}],
        )
        new_clins = TaskOrders.get_clins_for_create_billing_instructions()
        assert len(new_clins) == 0
