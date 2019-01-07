from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.task_order import TaskOrder
from atst.models.permissions import Permissions
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from .exceptions import NotFoundError

from atst.forms.task_order import AppInfoForm, FundingForm, OversightForm


class TaskOrderError(Exception):
    pass


class TaskOrders(object):
    SECTIONS = {
        "app_info": AppInfoForm,
        "funding": FundingForm,
        "oversight": OversightForm,
    }

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
        if section in TaskOrders.SECTIONS.keys():
            form = TaskOrders.SECTIONS[section]()

            form_fields = {}

            for attr in form.data:
                value = getattr(task_order, attr, None)
                if value is not None:
                    if value.__class__.__name__ == "date":
                        value = value.strftime("%m/%d/%Y")

                    form_fields[attr] = value

            checking_form = TaskOrders.SECTIONS[section](form_fields)
            is_valid = checking_form.validate_without_flash()

            form.validate_without_flash()

            if is_valid or checking_form.errors.keys() == {"csrf_token"}:
                return "complete"
            elif checking_form.errors == form.errors:
                return "incomplete"
            else:
                return "draft"

        else:
            return False

    @classmethod
    def all_sections_complete(cls, task_order):
        for section in TaskOrders.SECTIONS.keys():
            if (
                not TaskOrders.section_completion_status(task_order, section)
                == "complete"
            ):
                return False

        return True

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
