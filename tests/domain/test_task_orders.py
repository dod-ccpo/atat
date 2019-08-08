import pytest
from datetime import date, timedelta
from decimal import Decimal

from atst.domain.task_orders import TaskOrders
from atst.models.attachment import Attachment
from tests.factories import TaskOrderFactory, CLINFactory, PortfolioFactory


def test_task_order_sorting():
    """
    Task orders should be listed first by status, and then by time_created.
    """

    today = date.today()
    yesterday = today - timedelta(days=1)
    future = today + timedelta(days=100)

    task_orders = [
        # Draft
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        TaskOrderFactory.create(pdf=None),
        # Active
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=future)],
        ),
        # Upcoming
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=future, end_date=future)],
        ),
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
        TaskOrderFactory.create(
            signed_at=yesterday,
            clins=[CLINFactory.create(start_date=yesterday, end_date=yesterday)],
        ),
        # Unsigned
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
        TaskOrderFactory.create(
            clins=[CLINFactory.create(start_date=today, end_date=today)]
        ),
    ]

    assert TaskOrders.sort(task_orders) == task_orders


def test_create_adds_clins():
    portfolio = PortfolioFactory.create()
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "loas": ["123123123123", "345345234"],
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "loas": ["78979087"],
        },
    ]
    task_order = TaskOrders.create(
        creator=portfolio.owner,
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
            "loas": ["123123123123", "345345234"],
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "12312",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "loas": ["78979087"],
        },
    ]
    task_order = TaskOrders.create(
        creator=task_order.creator,
        portfolio_id=task_order.portfolio_id,
        number="0000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert task_order.number != to_number
    assert len(task_order.clins) == 2


def test_update_does_not_duplicate_clins():
    task_order = TaskOrderFactory.create(
        number="3453453456", create_clins=["123", "456"]
    )
    clins = [
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "123",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "loas": ["123123123123", "345345234"],
        },
        {
            "jedi_clin_type": "JEDI_CLIN_1",
            "number": "111",
            "start_date": date(2020, 1, 1),
            "end_date": date(2021, 1, 1),
            "obligated_amount": Decimal("5000"),
            "loas": ["78979087"],
        },
    ]
    task_order = TaskOrders.update(
        task_order_id=task_order.id,
        number="0000000000",
        clins=clins,
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    assert len(task_order.clins) == 2
    for clin in task_order.clins:
        assert clin.number != "456"
