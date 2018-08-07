from sqlalchemy import Column, func
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id


class Request(Base):
    __tablename__ = "requests"

    id = Id()
    creator = Column(UUID(as_uuid=True))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    body = Column(JSONB)
    status_events = relationship(
        "RequestStatusEvent", backref="request", order_by="RequestStatusEvent.sequence"
    )

    @property
    def status(self):
        return self.status_events[-1].new_status

    def set_status(self, status):
        self.status_events.append(status)

