from sqlalchemy import TIMESTAMP, Column


class ClaimableMixin(object):
    claimed_until = Column(TIMESTAMP(timezone=True))
