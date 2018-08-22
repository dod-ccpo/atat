from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from atst.models import Base
from atst.models.types import Id


class Request(Base):
    __tablename__ = "requests"

    id = Id()
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    body = Column(JSONB)
    status_events = relationship(
        "RequestStatusEvent", backref="request", order_by="RequestStatusEvent.sequence"
    )

    user_id = Column(ForeignKey("users.id"), nullable=False)
    creator = relationship("User")

    task_order_id = Column(ForeignKey("task_order.id"))
    task_order = relationship("TaskOrder")

    @property
    def status(self):
        return self.status_events[-1].new_status

    @property
    def status_displayname(self):
        return self.status_events[-1].displayname

    @property
    def annual_spend(self):
        monthly = self.body.get("details_of_use", {}).get("estimated_monthly_spend", 0)
        return monthly * 12
