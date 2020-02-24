from sqlalchemy import String, Column

from atat.models.base import Base
import atat.models.types as types
import atat.models.mixins as mixins


class NotificationRecipient(Base, mixins.TimestampsMixin):
    __tablename__ = "notification_recipients"

    id = types.Id()
    email = Column(String, nullable=False)
