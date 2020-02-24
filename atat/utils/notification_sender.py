from sqlalchemy import select

from atat.jobs import send_notification_mail
from atat.database import db
from atat.models.notification_recipient import NotificationRecipient


class NotificationSender(object):
    EMAIL_SUBJECT = "ATAT notification"

    def send(self, body, type_=None):
        recipients = self._get_recipients(type_)
        send_notification_mail.delay(recipients, self.EMAIL_SUBJECT, body)

    def _get_recipients(self, type_):
        query = select([NotificationRecipient.email])
        return db.session.execute(query).fetchone()
