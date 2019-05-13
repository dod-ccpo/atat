from atst.queue import ATSTQueue, queue
from atst.database import db
from atst.models import NotificationRecipient


class NotificationSender(object):
    EMAIL_SUBJECT = "ATST notification"

    def __init__(self, queue: ATSTQueue):
        self.queue = queue

    def send(self, body, type_=None):
        recipients = self._get_recipients(type_)
        self.queue.send_mail(recipients, self.EMAIL_SUBJECT, body)

    def _get_recipients(self, type_):
        return [
            recipient.email
            for recipient in db.session.query(NotificationRecipient).all()
        ]


notification_sender = NotificationSender(queue)
