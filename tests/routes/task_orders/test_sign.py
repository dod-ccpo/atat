from flask import url_for

from atst.domain.task_orders import TaskOrders
from tests.factories import UserFactory, TaskOrderFactory


def test_new_task_order(client, user_session):
    creator = UserFactory.create()
    user_session()
    task_order = TaskOrderFactory.create()
    response = client.get(
        url_for("task_orders.show_signature", task_order_id=task_order.id)
    )
    assert response.status_code == 200
