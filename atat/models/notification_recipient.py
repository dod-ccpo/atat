from sqlalchemy import Column, String

import atat.models.mixins as mixins
import atat.models.types as types
from atat.models.base import Base


class NotificationRecipient(Base, mixins.TimestampsMixin):
    __tablename__ = "notification_recipients"

    id = types.Id()
    email = Column(String, nullable=False)
