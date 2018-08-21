from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.database import db
from atst.models.task_order import TaskOrder, Source
from .exceptions import NotFoundError


class TaskOrders(object):

    @classmethod
    def get(cls, order_number):
        try:
            task_order = (
                db.session.query(TaskOrder).filter_by(number=order_number).one()
            )
        except NoResultFound:
            if TaskOrders._client():
                task_order = TaskOrders._get_from_eda(order_number)
            else:
                raise NotFoundError("task_order")

        return task_order

    @classmethod
    def _get_from_eda(cls, order_number):
        to_data = TaskOrders._client().get_contract(order_number, status="y")
        if to_data:
            # TODO: we need to determine exactly what we're getting and storing from the EDA client
            return TaskOrders.create(number=to_data["contract_no"], source=Source.EDA)
        else:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, **kwargs):
        task_order = TaskOrder(**kwargs)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def _client(cls):
        return app.eda_client
