from sqlalchemy.orm.exc import NoResultFound
from flask import current_app as app

from atst.database import db
from atst.models.task_order import TaskOrder
from atst.models.permissions import Permissions
from atst.models.dd_254 import DD254
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from .exceptions import NotFoundError


class TaskOrderError(Exception):
    pass


class TaskOrders(object):
    INFORMATION_RECORDED_ATTRIBUTES = ["end_date", "loa", "number", "start_date"]

    SECTIONS = {
        "app_info": [
            "portfolio_name",
            "scope",
            "defense_component",
            "app_migration",
            "native_apps",
            "complexity",
            "dev_team",
            "team_experience",
        ],
        "funding": [
            "performance_length",
            "csp_estimate",
            "clin_01",
            "clin_02",
            "clin_03",
            "clin_04",
        ],
        "oversight": [
            "ko_first_name",
            "ko_last_name",
            "ko_email",
            "ko_phone_number",
            "cor_first_name",
            "cor_last_name",
            "cor_email",
            "cor_phone_number",
            "so_first_name",
            "so_last_name",
            "so_email",
            "so_phone_number",
        ],
    }

    UNCLASSIFIED_FUNDING = ["performance_length", "csp_estimate", "clin_01", "clin_03"]

    @classmethod
    def get(cls, user, task_order_id):
        try:
            task_order = db.session.query(TaskOrder).filter_by(id=task_order_id).one()
            Authorization.check_task_order_permission(
                user, task_order, Permissions.VIEW_TASK_ORDER, "view task order"
            )

            return task_order
        except NoResultFound:
            raise NotFoundError("task_order")

    @classmethod
    def create(cls, creator, portfolio):
        Authorization.check_portfolio_permission(
            creator, portfolio, Permissions.UPDATE_TASK_ORDER, "add task order"
        )
        task_order = TaskOrder(portfolio=portfolio, creator=creator)

        db.session.add(task_order)
        db.session.commit()

        return task_order

    @classmethod
    def update(cls, user, task_order, **kwargs):
        Authorization.check_task_order_permission(
            user, task_order, Permissions.UPDATE_TASK_ORDER, "update task order"
        )

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
                if getattr(task_order, attr):
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
    def is_signed_by_ko(cls, task_order):
        return task_order.signer_dod_id is not None

    @classmethod
    def mission_owner_sections(cls):
        section_list = TaskOrders.SECTIONS
        if not app.config.get("CLASSIFIED"):
            section_list["funding"] = TaskOrders.UNCLASSIFIED_FUNDING
        return section_list

    OFFICERS = [
        "contracting_officer",
        "contracting_officer_representative",
        "security_officer",
    ]

    @classmethod
    def add_officer(cls, user, task_order, officer_type, officer_data):
        Authorization.check_portfolio_permission(
            user,
            task_order.portfolio,
            Permissions.ADD_TASK_ORDER_OFFICER,
            "add task order officer",
        )

        if officer_type in TaskOrders.OFFICERS:
            portfolio = task_order.portfolio

            existing_member = next(
                (
                    member
                    for member in portfolio.members
                    if member.user.dod_id == officer_data["dod_id"]
                ),
                None,
            )

            if existing_member:
                portfolio_user = existing_member.user
            else:
                member = Portfolios.create_member(
                    user, portfolio, {**officer_data, "portfolio_role": "officer"}
                )
                portfolio_user = member.user

            setattr(task_order, officer_type, portfolio_user)

            db.session.add(task_order)
            db.session.commit()

            return portfolio_user
        else:
            raise TaskOrderError(
                "{} is not an officer role on task orders".format(officer_type)
            )

    @classmethod
    def add_dd_254(user, task_order, dd_254_data):
        dd_254 = DD254(**dd_254_data)
        task_order.dd_254 = dd_254

        db.session.add(task_order)
        db.session.commit()


class DD254s:
    # TODO: standin implementation until we have a real download,
    # sign, and verify process for the DD 254 PDF
    @classmethod
    def is_complete(cls, dd254):
        if dd254 is None:
            return False

        for col in DD254.__table__.columns:
            if getattr(dd254, col.name) is None:
                return False

        return True
