import pendulum
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from atat.database import db
from atat.models import (
    CLIN,
    Portfolio,
    PortfolioStateMachine,
    PortfolioStates,
    TaskOrder,
)
from atat.models.task_order import SORT_ORDERING
from atat.utils import commit_or_raise_already_exists_error

from . import BaseDomainClass


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
        task_order.signed_at = pendulum.now(tz="UTC")
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
            .options(joinedload(TaskOrder.pdf))
            .join(CLIN)
            .filter(
                or_(
                    TaskOrder.pdf_last_sent_at < CLIN.last_sent_at,
                    TaskOrder.pdf_last_sent_at.is_(None),
                )
            )
            .all()
        )

    @classmethod
    def get_clins_for_create_billing_instructions(cls):
        """Finds CLINs that need to be transmitted to the CSP. These should be
        CLINs that have changed since the portfolio was initially provisioned.
        CLINs are not updated in-place, just updated entirely when a user edits
        them. Because of this, the last_sent_at column will always be empty for
        a new or "edited" CLIN.

        Checks that:
          - last_sent_at is null
          - the current date is within the CLIN's period of performance
          - the associated portfolio is done being provisioned
        """

        return (
            db.session.query(CLIN)
            .join(TaskOrder)
            .join(Portfolio)
            .join(PortfolioStateMachine)
            .filter(
                CLIN.last_sent_at.is_(None),
                CLIN.start_date <= func.now(),
                CLIN.end_date >= func.now(),
                PortfolioStateMachine.state == PortfolioStates.COMPLETED,
            )
            .all()
        )
