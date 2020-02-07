from datetime import datetime
from sqlalchemy import or_

from atst.database import db
from atst.models.clin import CLIN
from atst.models.task_order import TaskOrder, SORT_ORDERING
from . import BaseDomainClass
from atst.utils import commit_or_raise_already_exists_error


class TaskOrders(BaseDomainClass):
    model = TaskOrder
    resource_name = "task_order"

    @classmethod
    def create(cls, portfolio_id, number, clins, pdf):
        task_order = TaskOrder(portfolio_id=portfolio_id, number=number, pdf=pdf)
        db.session.add(task_order)
        commit_or_raise_already_exists_error(message="task_order")
        TaskOrders.create_clins(task_order.id, clins)
        return task_order

    @classmethod
    def update(cls, task_order_id, number, clins, pdf):
        task_order = TaskOrders.get(task_order_id)
        task_order.pdf = pdf

        if len(clins) > 0:
            for clin in task_order.clins:
                db.session.delete(clin)

            TaskOrders.create_clins(task_order_id, clins)

        if number != task_order.number:
            task_order.number = number
            db.session.add(task_order)

        commit_or_raise_already_exists_error(message="task_order")
        return task_order

    @classmethod
    def sign(cls, task_order, signer_dod_id):
        task_order.signer_dod_id = signer_dod_id
        task_order.signed_at = datetime.now()

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def create_clins(cls, task_order_id, clin_list):
        for clin_data in clin_list:
            clin = CLIN(
                task_order_id=task_order_id,
                number=clin_data["number"],
                start_date=clin_data["start_date"],
                end_date=clin_data["end_date"],
                total_amount=clin_data["total_amount"],
                obligated_amount=clin_data["obligated_amount"],
                jedi_clin_type=clin_data["jedi_clin_type"],
            )
            db.session.add(clin)
            db.session.commit()

    @classmethod
    def sort_by_status(cls, task_orders):
        by_status = {status.value: [] for status in SORT_ORDERING}

        for task_order in task_orders:
            by_status[task_order.display_status].append(task_order)

        return by_status

    @classmethod
    def delete(cls, task_order_id):
        task_order = TaskOrders.get(task_order_id)
        db.session.delete(task_order)
        db.session.commit()

    @classmethod
    def get_for_send_task_order_files(cls):
        return (
            db.session.query(TaskOrder)
            .join(CLIN)
            .filter(
                or_(
                    TaskOrder.pdf_last_sent_at < CLIN.last_sent_at,
                    TaskOrder.pdf_last_sent_at.is_(None),
                )
            )
            .all()
        )
