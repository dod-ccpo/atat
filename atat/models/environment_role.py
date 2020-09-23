from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import atat.models.mixins as mixins
import atat.models.types as types
from atat.models.base import Base


class CSPRole(Enum):
    ADMIN = "Admin"
    BILLING_READ = "Billing Read-only"
    CONTRIBUTOR = "Contributor"


class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"


class EnvironmentRole(
    Base,
    mixins.TimestampsMixin,
    mixins.AuditableMixin,
    mixins.DeletableMixin,
    mixins.ClaimableMixin,
):
    __tablename__ = "environment_roles"

    id = types.Id()
    environment_id = Column(
        UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False
    )
    environment = relationship("Environment")

    role = Column(SQLAEnum(CSPRole, native_enum=False), nullable=True)

    application_role_id = Column(
        UUID(as_uuid=True), ForeignKey("application_roles.id"), nullable=False
    )
    application_role = relationship("ApplicationRole")

    cloud_id = Column(String())

    status = Column(
        SQLAEnum(Status, native_enum=False), default=Status.PENDING, nullable=False
    )

    def __repr__(self):
        return "<EnvironmentRole(role='{}', user='{}', environment='{}', id='{}')>".format(
            self.role, self.application_role.user_name, self.environment.name, self.id
        )

    @property
    def history(self):
        return self.get_changes()

    @property
    def portfolio_id(self):
        return self.environment.portfolio_id

    @property
    def application_id(self):
        return self.environment.application_id

    @property
    def displayname(self):
        return self.role

    @property
    def is_disabled(self):
        return self.status == Status.DISABLED

    @property
    def is_pending(self):
        return self.status == Status.PENDING

    @property
    def event_details(self):
        return {
            "updated_user_name": self.application_role.user_name,
            "updated_application_role_id": str(self.application_role_id),
            "role": self.role,
            "environment": self.environment.displayname,
            "environment_id": str(self.environment_id),
            "application": self.environment.application.name,
            "application_id": str(self.environment.application_id),
            "portfolio": self.environment.portfolio.name,
            "portfolio_id": str(self.environment.portfolio.id),
        }


Index(
    "environments_role_user_environment",
    EnvironmentRole.application_role_id,
    EnvironmentRole.environment_id,
    unique=True,
)
