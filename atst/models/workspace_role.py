from sqlalchemy import Index, ForeignKey, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from atst.models import Base
from .types import Id


class WorkspaceRole(Base):
    __tablename__ = "workspace_role"

    id = Id()
    workspace_id = Column(UUID(as_uuid=True), index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    role = relationship("Role")


Index(
    "workspace_role_user_workspace",
    WorkspaceRole.user_id,
    WorkspaceRole.workspace_id,
    unique=True,
)
