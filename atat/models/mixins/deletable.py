from sqlalchemy import Column, Boolean
from sqlalchemy.sql import expression


class DeletableMixin(object):
    deleted = Column(Boolean, nullable=False, server_default=expression.false())
