from sqlalchemy import Column, func, ForeignKey
from sqlalchemy.types import DateTime, String, BigInteger
from sqlalchemy.schema import Sequence
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base
from atst.models.types import Id


class RequestStatusEvent(Base):
    __tablename__ = 'request_status_events'

    id = Id()
    new_status = Column(String())
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    request_id = Column(UUID(as_uuid=True), ForeignKey('requests.id', ondelete='CASCADE'))
    sequence = Column(BigInteger, Sequence('request_status_events_sequence_seq'), nullable=False)
