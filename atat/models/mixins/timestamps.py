from sqlalchemy import Column, func, TIMESTAMP


class TimestampsMixin(object):
    time_created = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now(tz="UTC")
    )
    time_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(tz="UTC"),
        onupdate=func.current_timestamp(),
    )
