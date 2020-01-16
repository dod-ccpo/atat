from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY
from itertools import chain

from atst.models.base import Base
import atst.models.types as types
import atst.models.mixins as mixins
from atst.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atst.domain.permission_sets import PermissionSets
from atst.utils import first_or_none
from atst.database import db

from sqlalchemy_json import NestedMutableJson


class Portfolio(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    __tablename__ = "portfolios"

    id = types.Id()
    name = Column(String, nullable=False)
    defense_component = Column(
        String, nullable=False
    )  # Department of Defense Component

    app_migration = Column(String)  # App Migration
    complexity = Column(ARRAY(String))  # Application Complexity
    complexity_other = Column(String)
    description = Column(String)
    dev_team = Column(ARRAY(String))  # Development Team
    dev_team_other = Column(String)
    native_apps = Column(String)  # Native Apps
    team_experience = Column(String)  # Team Experience

    csp_data = Column(NestedMutableJson, nullable=True)

    applications = relationship(
        "Application",
        back_populates="portfolio",
        primaryjoin="and_(Application.portfolio_id == Portfolio.id, Application.deleted == False)",
    )

    state_machine = relationship(
        "PortfolioStateMachine", uselist=False, back_populates="portfolio"
    )

    roles = relationship("PortfolioRole")

    task_orders = relationship("TaskOrder")

    @property
    def owner_role(self):
        def _is_portfolio_owner(portfolio_role):
            return PermissionSets.PORTFOLIO_POC in [
                perms_set.name for perms_set in portfolio_role.permission_sets
            ]

        return first_or_none(_is_portfolio_owner, self.roles)

    @property
    def owner(self):
        owner_role = self.owner_role
        return owner_role.user if owner_role else None

    @property
    def users(self):
        return set(role.user for role in self.roles)

    @property
    def user_count(self):
        return len(self.members)

    @property
    def num_task_orders(self):
        return len(self.task_orders)

    @property
    def active_clins(self):
        return [
            clin
            for task_order in self.task_orders
            for clin in task_order.clins
            if clin.is_active
        ]

    @property
    def active_task_orders(self):
        return [task_order for task_order in self.task_orders if task_order.is_active]

    @property
    def funding_duration(self):
        """
        Return the earliest period of performance start date and latest period
        of performance end date for all active task orders in a portfolio.
        @return: (datetime.date or None, datetime.date or None)
        """
        start_dates = (
            task_order.start_date
            for task_order in self.task_orders
            if task_order.is_active
        )

        end_dates = (
            task_order.end_date
            for task_order in self.task_orders
            if task_order.is_active
        )

        earliest_pop_start_date = min(start_dates, default=None)
        latest_pop_end_date = max(end_dates, default=None)

        return (earliest_pop_start_date, latest_pop_end_date)

    @property
    def days_to_funding_expiration(self):
        """
        Returns the number of days between today and the lastest period performance
        end date of all active Task Orders
        """
        return max(
            (
                task_order.days_to_expiration
                for task_order in self.task_orders
                if task_order.is_active
            ),
            default=0,
        )

    @property
    def members(self):
        return (
            db.session.query(PortfolioRole)
            .filter(PortfolioRole.portfolio_id == self.id)
            .filter(PortfolioRole.status != PortfolioRoleStatus.DISABLED)
            .all()
        )

    @property
    def displayname(self):
        return self.name

    @property
    def all_environments(self):
        return list(chain.from_iterable(p.environments for p in self.applications))

    @property
    def portfolio_id(self):
        return self.id

    @property
    def application_id(self):
        return None

    def __repr__(self):
        return "<Portfolio(name='{}', user_count='{}', id='{}')>".format(
            self.name, self.user_count, self.id
        )
