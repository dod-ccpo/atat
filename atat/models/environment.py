from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

import atat.models.mixins as mixins
import atat.models.types as types
from atat.models.base import Base


class Environment(
    Base,
    mixins.TimestampsMixin,
    mixins.AuditableMixin,
    mixins.DeletableMixin,
    mixins.ClaimableMixin,
):
    __tablename__ = "environments"

    id = types.Id()
    name = Column(String, nullable=False)

    application_id = Column(ForeignKey("applications.id"), nullable=False)
    application = relationship("Application")

    # User user.id as the foreign key here beacuse the Environment creator may
    # not have an application role. We may need to revisit this if we receive any
    # requirements around tracking an environment's custodian.
    creator_id = Column(ForeignKey("users.id"), nullable=False)
    creator = relationship("User")

    cloud_id = Column(String)

    roles = relationship(
        "EnvironmentRole",
        back_populates="environment",
        primaryjoin="and_(EnvironmentRole.environment_id == Environment.id, EnvironmentRole.deleted == False)",
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "application_id", name="environments_name_application_id_key"
        ),
    )

    @property
    def users(self):
        return {r.application_role.user for r in self.roles}

    @property
    def num_users(self):
        return len(self.users)

    @property
    def displayname(self):
        return self.name

    @property
    def portfolio(self):
        return self.application.portfolio

    @property
    def portfolio_id(self):
        return self.application.portfolio_id

    @property
    def is_pending(self):
        return self.cloud_id is None

    def __repr__(self):
        return "<Environment(name='{}', num_users='{}', application='{}', portfolio='{}', id='{}')>".format(
            self.name,
            self.num_users,
            getattr(self, "application.name", None),
            getattr(self, "portfolio.name", None),
            self.id,
        )

    @property
    def history(self):
        return self.get_changes()
