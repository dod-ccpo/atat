from flask import current_app as app

from atst.database import db
from atst.models.task_order import TaskOrder, SORT_ORDERING
from . import BaseDomainClass


class TaskOrderError(Exception):
    pass


class TaskOrders(BaseDomainClass):
    model = TaskOrder
    resource_name = "task_order"

    SECTIONS = {"app_info": ["portfolio_name"], "funding": [], "oversight": []}

    UNCLASSIFIED_FUNDING = []

    @classmethod
    def create(cls, creator, portfolio_id, **kwargs):
        task_order = TaskOrder(portfolio_id=portfolio_id, creator=creator)
        for key, value in kwargs.items():
            setattr(task_order, key, value)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def update(cls, task_order_id, **kwargs):
        task_order = TaskOrders.get(task_order_id)
        for key, value in kwargs.items():
            setattr(task_order, key, value)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def section_completion_status(cls, task_order, section):
        if section in TaskOrders.mission_owner_sections():
            passed = []
            failed = []

            for attr in TaskOrders.SECTIONS[section]:
                if getattr(task_order, attr) is not None:
                    passed.append(attr)
                else:
                    failed.append(attr)

            if not failed:
                return "complete"
            elif passed and failed:
                return "draft"

        return "incomplete"

    @classmethod
    def all_sections_complete(cls, task_order):
        for section in TaskOrders.SECTIONS.keys():
            if (
                TaskOrders.section_completion_status(task_order, section)
                is not "complete"
            ):
                return False

        return True

    @classmethod
    def mission_owner_sections(cls):
        section_list = TaskOrders.SECTIONS
        if not app.config.get("CLASSIFIED"):
            section_list["funding"] = TaskOrders.UNCLASSIFIED_FUNDING
        return section_list

    @classmethod
    def sort(cls, task_orders: [TaskOrder]) -> [TaskOrder]:
        # Sorts a list of task orders on two keys: status (primary) and time_created (secondary)
        by_time_created = sorted(task_orders, key=lambda to: to.time_created)
        by_status = sorted(by_time_created, key=lambda to: SORT_ORDERING.get(to.status))
        return by_status
