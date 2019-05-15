from flask_rq2 import RQ
from flask import current_app as app


class ATSTQueue(RQ):

    """Internal helpers to get the queue that actually does the work.

    The RQ object always uses the "default" queue, unless we explicitly request
    otherwise. These helpers allow us to use `.queue_name` to get the name of
    the configured queue and `_queue_job` will use the appropriate queue.

    """

    @property
    def queue_name(self):
        return self.queues[0]

    def get_queue(self, name=None):
        if not name:
            name = self.queue_name
        return super().get_queue(name)

    def _queue_job(self, function, *args, **kwargs):
        self.get_queue().enqueue(function, *args, **kwargs)

    # pylint: disable=pointless-string-statement
    """Instance methods to queue up application-specific jobs."""

    def send_mail(self, recipients, subject, body):
        self._queue_job(ATSTQueue._send_mail, recipients, subject, body)

    def send_notification_mail(self, recipients, subject, body):
        self._queue_job(ATSTQueue._send_notification_mail, recipients, subject, body)

    # pylint: disable=pointless-string-statement
    """Class methods to actually perform the work.

    Must be a class method (or a module-level function) because we being able
    to pickle the class is more effort than its worth.
    """

    @classmethod
    def _send_mail(self, recipients, subject, body):
        app.mailer.send(recipients, subject, body)

    @classmethod
    def _send_notification_mail(self, recipients, subject, body):
        app.logger.info(
            "Sending a notification to these recipients: {}\n\n{}".format(
                recipients, body
            )
        )
        app.mailer.send(recipients, subject, body)


queue = ATSTQueue()
