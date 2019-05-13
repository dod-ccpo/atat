from logging import Logger

from atst.queue import ATSTQueue
from atst.database import db
from atst.models import NotificationRecipient


class NotificationSender(object):
    EMAIL_SUBJECT = "ATST notification"

    def __init__(self, queue: ATSTQueue, logger: Logger):
        self.queue = queue
        self.logger = logger

    def send(self, body, type_=None):
        recipients = self._get_recipients(type_)
        self.logger.info(
            "Sending a notification to these recipients: {}\n\n{}".format(recipients, body))
        self.queue.send_mail(recipients, self.EMAIL_SUBJECT, body)

    def _get_recipients(self, type_):
        return [
            recipient.email
            for recipient in db.session.query(NotificationRecipient).all()
        ]
