from sqlalchemy import select

from atst.queue import ATSTQueue
from atst.database import db
from atst.models import NotificationRecipient


class NotificationSender(object):
    EMAIL_SUBJECT = "ATST notification"

    def __init__(self, queue: ATSTQueue):
        self.queue = queue

    def send(self, body, type_=None):
        recipients = self._get_recipients(type_)
        self.queue.send_notification_mail(recipients, self.EMAIL_SUBJECT, body)

    def _get_recipients(self, type_):
        query = select([NotificationRecipient.email])
        return db.session.execute(query).fetchone()
