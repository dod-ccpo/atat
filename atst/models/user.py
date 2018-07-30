from sqlalchemy import String, ForeignKey, Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from atst.models import Base
from .types import Id


class User(Base):
    __tablename__ = "users"

    id = Id()
    username = Column(String)
    atat_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))

    atat_role = relationship("Role")
    workspace_roles = relationship("WorkspaceRole", backref="user")

    @property
    def atat_permissions(self):
        return self.atat_role.permissions
