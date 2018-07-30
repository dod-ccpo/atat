from sqlalchemy.orm.exc import NoResultFound

from atst.models.task_order import TaskOrder
from .exceptions import NotFoundError


class TaskOrders(object):

    def __init__(self, db_session):
        self.db_session = db_session

    def get(self, order_number):
        try:
            task_order = self.db_session.query(TaskOrder).filter_by(number=order_number).one()
        except NoResultFound:
            raise NotFoundError("task_order")

        return task_order
