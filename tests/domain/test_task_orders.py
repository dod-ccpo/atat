import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from atst.domain.exceptions import AlreadyExistsError
from atst.domain.task_orders import TaskOrders
from atst.models import Attachment
from atst.models.task_order import TaskOrder, SORT_ORDERING, Status
from tests.factories import TaskOrderFactory, CLINFactory, PortfolioFactory


def test_create_adds_clins():
    portfolio = PortfolioFactory.create()
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
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
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
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
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "total_amount": Decimal("10000"),
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "111",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
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
    today = date.today()
    yesterday = today - timedelta(days=1)
    future = today + timedelta(days=100)

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
    assert len(sorted_by_status["Draft"]) == 3
    assert len(sorted_by_status["Active"]) == 1
    assert len(sorted_by_status["Upcoming"]) == 1
    assert len(sorted_by_status["Expired"]) == 2
    assert len(sorted_by_status["Unsigned"]) == 1
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


def test_get_for_send_task_order_files():
    new_to = TaskOrderFactory.create(create_clins=[{}])
    updated_to = TaskOrderFactory.create(
        create_clins=[{"last_sent_at": datetime(2020, 2, 1)}],
        pdf_last_sent_at=datetime(2020, 1, 1),
    )
    sent_to = TaskOrderFactory.create(
        create_clins=[{"last_sent_at": datetime(2020, 1, 1)}],
        pdf_last_sent_at=datetime(2020, 1, 1),
    )

    updated_and_new_task_orders = TaskOrders.get_for_send_task_order_files()
    assert len(updated_and_new_task_orders) == 2
    assert sent_to not in updated_and_new_task_orders
    assert updated_to in updated_and_new_task_orders
    assert new_to in updated_and_new_task_orders
