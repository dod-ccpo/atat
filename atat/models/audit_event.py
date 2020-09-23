from sqlalchemy import Column, ForeignKey, String, inspect
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

import atat.models.types as types
from atat.models.base import Base
from atat.models.mixins.timestamps import TimestampsMixin


class AuditEvent(Base, TimestampsMixin):
    __tablename__ = "audit_events"

    id = types.Id()

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="audit_events")

    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), index=True)
    portfolio = relationship("Portfolio", backref="audit_events")

    application_id = Column(
        UUID(as_uuid=True), ForeignKey("applications.id"), index=True
    )
    application = relationship("Application", backref="audit_events")

    changed_state = Column(JSONB())
    event_details = Column(JSONB())

    resource_type = Column(String(), nullable=False)
    resource_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    display_name = Column(String())
    action = Column(String(), nullable=False)

    @property
    def log(self):
        return {
            "portfolio_id": str(self.portfolio_id),
            "application_id": str(self.application_id),
            "changed_state": self.changed_state,
            "event_details": self.event_details,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id),
            "display_name": self.display_name,
            "action": self.action,
        }

    def save(self, connection):
        attrs = inspect(self).dict

        connection.execute(self.__table__.insert(), **attrs)

    def __repr__(self):  # pragma: no cover
        return "<AuditEvent(name='{}', action='{}', id='{}')>".format(
            self.display_name, self.action, self.id
        )
