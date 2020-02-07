from flask import g
from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.domain.authz import Authorization
from atst.domain.exceptions import NotFoundError
from atst.domain.portfolios.scopes import ScopedPortfolio
from atst.models import (
    Application,
    Environment,
    Permissions,
    Portfolio,
    PortfolioInvitation,
    PortfolioRole,
    TaskOrder,
)


def get_resources_from_context(view_args):
    query = None

    if view_args is None:
        view_args = {}

    if "portfolio_token" in view_args:
        query = (
            db.session.query(Portfolio)
            .join(PortfolioRole, PortfolioRole.portfolio_id == Portfolio.id)
            .join(
                PortfolioInvitation,
                PortfolioInvitation.portfolio_role_id == PortfolioRole.id,
            )
            .filter(PortfolioInvitation.token == view_args["portfolio_token"])
        )

    elif "portfolio_id" in view_args:
        query = db.session.query(Portfolio).filter(
            Portfolio.id == view_args["portfolio_id"]
        )

    elif "application_id" in view_args:
        query = (
            db.session.query(Portfolio, Application)
            .join(Application, Application.portfolio_id == Portfolio.id)
            .filter(Application.id == view_args["application_id"])
        )

    elif "environment_id" in view_args:
        query = (
            db.session.query(Portfolio, Application)
            .join(Application, Application.portfolio_id == Portfolio.id)
            .join(Environment, Environment.application_id == Application.id)
            .filter(Environment.id == view_args["environment_id"])
        )

    elif "task_order_id" in view_args:
        query = (
            db.session.query(Portfolio, TaskOrder)
            .join(TaskOrder, TaskOrder.portfolio_id == Portfolio.id)
            .filter(TaskOrder.id == view_args["task_order_id"])
        )

    if query:
        try:
            return query.only_return_tuples(True).one()
        except NoResultFound:
            raise NotFoundError("portfolio")


def assign_resources(view_args):
    g.portfolio = None
    g.application = None
    g.task_order = None

    resources = get_resources_from_context(view_args)
    if resources:
        for resource in resources:
            if isinstance(resource, Portfolio):
                g.portfolio = ScopedPortfolio(g.current_user, resource)
            elif isinstance(resource, Application):
                g.application = resource
            elif isinstance(resource, TaskOrder):
                g.task_order = resource


def user_can_view(permission):
    if g.application:
        return Authorization.has_application_permission(
            g.current_user, g.application, permission
        )
    elif g.portfolio:
        return Authorization.has_portfolio_permission(
            g.current_user, g.portfolio, permission
        )
    else:
        return Authorization.has_atat_permission(g.current_user, permission)


def portfolio():
    if g.current_user is None:
        return {}
    elif g.portfolio is not None:
        active_task_orders = [
            task_order for task_order in g.portfolio.task_orders if task_order.is_active
        ]
        funding_end_date = (
            # TODO: fix task order -- reimplement logic to get end date from CLINs
            # sorted(active_task_orders, key=attrgetter("end_date"))[-1].end_date
            # if active_task_orders
            # else None
            None
        )
        funded = len(active_task_orders) > 1
    else:
        funding_end_date = None
        funded = None

    return {
        "portfolio": g.portfolio,
        "permissions": Permissions,
        "user_can": user_can_view,
        "funding_end_date": funding_end_date,
        "funded": funded,
    }


def atat():
    return {"permissions": Permissions, "user_can": user_can_view}
