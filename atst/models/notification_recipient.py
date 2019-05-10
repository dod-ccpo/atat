from sqlalchemy import String, Column

from atst.models import Base, types, mixins


class NotificationRecipient(Base, mixins.TimestampsMixin):
    __tablename__ = "notification_recipients"

    id = types.Id()
    email = Column(String, nullable=False)
