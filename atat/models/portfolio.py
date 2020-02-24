import re
from itertools import chain
from random import choices
from string import ascii_lowercase, digits
from typing import Dict

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY
from sqlalchemy_json import NestedMutableJson

from atat.database import db
import atat.models.mixins as mixins
import atat.models.types as types
from atat.domain.csp.cloud.utils import generate_mail_nickname
from atat.domain.permission_sets import PermissionSets
from atat.models.base import Base
from atat.models.portfolio_role import PortfolioRole, Status as PortfolioRoleStatus
from atat.utils import first_or_none


class Portfolio(
    Base, mixins.TimestampsMixin, mixins.AuditableMixin, mixins.DeletableMixin
):
    __tablename__ = "portfolios"

    id = types.Id()
    name = Column(String, nullable=False)
    defense_component = Column(
        ARRAY(String), nullable=False
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
    clins = relationship("CLIN", secondary="task_orders")

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
    def initial_clin_dict(self) -> Dict:
        initial_clin = min(
            (
                clin
                for clin in self.clins
                if (clin.is_active and clin.task_order.is_signed)
            ),
            key=lambda clin: clin.start_date,
            default=None,
        )
        if initial_clin:
            return {
                "initial_task_order_id": initial_clin.task_order.number,
                "initial_clin_number": initial_clin.number,
                "initial_clin_type": initial_clin.jedi_clin_number,
                "initial_clin_amount": initial_clin.obligated_amount,
                "initial_clin_start_date": initial_clin.start_date.strftime("%Y/%m/%d"),
                "initial_clin_end_date": initial_clin.end_date.strftime("%Y/%m/%d"),
            }
        else:
            return {}

    @property
    def active_task_orders(self):
        return [task_order for task_order in self.task_orders if task_order.is_active]

    @property
    def total_obligated_funds(self):
        return sum(
            (task_order.total_obligated_funds for task_order in self.active_task_orders)
        )

    @property
    def upcoming_obligated_funds(self):
        return sum(
            (
                task_order.total_obligated_funds
                for task_order in self.task_orders
                if task_order.is_upcoming
            )
        )

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
    def domain_name(self):
        """
        CSP domain name associated with portfolio.
        If a domain name is not set, generate one.
        """
        domain_name = re.sub("[^0-9a-zA-Z]+", "", self.name).lower() + "".join(
            choices(ascii_lowercase + digits, k=4)
        )
        if self.csp_data:
            return self.csp_data.get("domain_name", domain_name)
        else:
            return domain_name

    @property
    def application_id(self):
        return None

    def to_dictionary(self):
        return {
            "user_id": generate_mail_nickname(
                f"{self.owner.first_name[0]}{self.owner.last_name}"
            ),
            "password": "",
            "domain_name": self.domain_name,
            "first_name": self.owner.first_name,
            "last_name": self.owner.last_name,
            "country_code": "US",
            "password_recovery_email_address": self.owner.email,
            "address": {  # TODO: TBD if we're sourcing this from data or config
                "company_name": "",
                "address_line_1": "",
                "city": "",
                "region": "",
                "country": "",
                "postal_code": "",
            },
            "billing_profile_display_name": "ATAT Billing Profile",
            **self.initial_clin_dict,
        }

    def __repr__(self):
        return "<Portfolio(name='{}', user_count='{}', id='{}')>".format(
            self.name, self.user_count, self.id
        )
