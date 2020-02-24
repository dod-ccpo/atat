from sqlalchemy import Column, TIMESTAMP


class ClaimableMixin(object):
    claimed_until = Column(TIMESTAMP(timezone=True))
