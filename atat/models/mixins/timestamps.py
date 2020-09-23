from sqlalchemy import TIMESTAMP, Column, func


class TimestampsMixin(object):
    time_created = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    time_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.current_timestamp(),
    )
