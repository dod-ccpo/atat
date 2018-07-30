from sqlalchemy import String, Column
from sqlalchemy.dialects.postgresql import ARRAY

from atst.models import Base
from .types import Id


class Role(Base):
    __tablename__ = "roles"

    id = Id()
    name = Column(String, index=True, unique=True)
    description = Column(String)
    permissions = Column(ARRAY(String), index=True, server_default="{}")
