from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

import atat.models.mixins as mixins
from atat.models.base import Base


class PortfolioInvitation(
    Base, mixins.TimestampsMixin, mixins.InvitesMixin, mixins.AuditableMixin
):
    __tablename__ = "portfolio_invitations"

    portfolio_role_id = Column(
        UUID(as_uuid=True), ForeignKey("portfolio_roles.id"), index=True, nullable=False
    )
    role = relationship(
        "PortfolioRole",
        backref=backref("invitations", order_by="PortfolioInvitation.time_created"),
    )

    @property
    def portfolio(self):
        if self.role:  # pragma: no branch
            return self.role.portfolio

    @property
    def portfolio_id(self):
        return self.role.portfolio_id

    @property
    def application_id(self):
        return None
