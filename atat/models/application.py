from sqlalchemy import and_, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship, synonym

from atat.models.base import Base
from atat.models.application_role import ApplicationRole
from atat.models.environment import Environment
from atat.models import mixins
from atat.models.types import Id


class Application(
    Base,
    mixins.TimestampsMixin,
    mixins.AuditableMixin,
    mixins.DeletableMixin,
    mixins.ClaimableMixin,
):
    __tablename__ = "applications"

    id = Id()
    name = Column(String, nullable=False)
    description = Column(String)

    portfolio_id = Column(ForeignKey("portfolios.id"), nullable=False)
    portfolio = relationship("Portfolio")
    environments = relationship(
        "Environment",
        back_populates="application",
        primaryjoin=and_(
            Environment.application_id == id, Environment.deleted == False
        ),
        order_by="Environment.name",
    )
    roles = relationship(
        "ApplicationRole",
        primaryjoin=and_(
            ApplicationRole.application_id == id, ApplicationRole.deleted == False
        ),
    )
    members = synonym("roles")
    __table_args__ = (
        UniqueConstraint(
            "name", "portfolio_id", name="applications_name_portfolio_id_key"
        ),
    )

    cloud_id = Column(String)

    @property
    def users(self):
        return set(role.user for role in self.members)

    @property
    def displayname(self):
        return self.name

    @property
    def application_id(self):
        return self.id

    def __repr__(self):  # pragma: no cover
        return "<Application(name='{}', description='{}', portfolio='{}', id='{}')>".format(
            self.name, self.description, self.portfolio.name, self.id
        )

    @property
    def history(self):
        return self.get_changes()
