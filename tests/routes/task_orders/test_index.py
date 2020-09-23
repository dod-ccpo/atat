import pytest
from flask import url_for

from atat.domain.permission_sets import PermissionSets
from atat.domain.task_orders import TaskOrders
from atat.models import *
from atat.models.portfolio_role import Status as PortfolioStatus
from atat.models.task_order import Status as TaskOrderStatus
from atat.utils.localization import translate
from tests.factories import *
from tests.utils import captured_templates


@pytest.fixture
def portfolio():
    return PortfolioFactory.create()


@pytest.fixture
def user():
    return UserFactory.create()


@pytest.fixture
def task_order():
    user = UserFactory.create()
    portfolio = PortfolioFactory.create(owner=user)
    attachment = Attachment(filename="sample_attachment", object_name="sample")
    task_order = TaskOrderFactory.create(portfolio=portfolio)
    CLINFactory.create(task_order=task_order)

    return task_order


def test_view_task_order_not_draft(client, user_session, task_order):
    user = UserFactory()
    TaskOrders.sign(task_order=task_order, signer_dod_id=user.dod_id)
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.view_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 200


def test_view_task_order_draft(client, user_session, task_order):
    TaskOrders.update(
        task_order_id=task_order.id,
        number="1234567890",
        clins=[],
        pdf={"filename": "sample.pdf", "object_name": "1234567"},
    )
    user_session(task_order.portfolio.owner)
    response = client.get(
        url_for("task_orders.view_task_order", task_order_id=task_order.id)
    )
    assert response.status_code == 302
    assert url_for("task_orders.edit", task_order_id=task_order.id) in response.location
