import pytest
from atat.utils.mailer import (
    Mailer,
    MailConnection,
    RedisConnection,
)
from atat.utils.localization import translate
from email.mime.base import MIMEBase


class MockConnection(MailConnection):
    def __init__(self):
        self._messages = []
        self.sender = "mock@mock.com"

    def send(self, message):
        self._messages.append(message)

    @property
    def messages(self):
        return self._messages


@pytest.fixture
def mailer():
    return Mailer(MockConnection(), "test@atat.com")


def test_mailer_can_send_mail(mailer):
    message_data = {
        "recipients": ["ben@tattoine.org"],
        "subject": "help",
        "body": "you're my only hope",
    }
    mailer.send(**message_data)
    assert len(mailer.messages) == 1
    message = mailer.messages[0]
    assert message["To"] == message_data["recipients"][0]
    assert message["Subject"] == message_data["subject"]
    assert message.get_content().strip() == message_data["body"]


def test_redis_mailer_can_save_messages(app):
    mailer = Mailer(RedisConnection(app.redis), "test@atat.com")
    message_data = {
        "recipients": ["ben@tattoine.org"],
        "subject": "help",
        "body": "you're my only hope",
    }
    mailer.send(**message_data)
    assert len(mailer.messages) == 1
    message = mailer.messages[0]
    assert message_data["recipients"][0] in message
    assert message_data["subject"] in message
    assert message_data["body"] in message


def test_send_with_attachment(app, mailer, downloaded_task_order):
    to_number = "11111111111111"
    attachment = {
        "maintype": "application",
        "subtype": "pdf",
        "filename": downloaded_task_order["name"],
        "content": downloaded_task_order["content"],
    }
    mailer.send(
        recipients=[app.config["MICROSOFT_TASK_ORDER_EMAIL_ADDRESS"]],
        subject=translate("email.task_order_sent.subject", {"to_number": to_number}),
        body=translate("email.task_order_sent.body", {"to_number": to_number}),
        attachments=[attachment],
    )
    # one email was sent
    assert len(mailer.messages) == 1

    # the email was sent to Microsoft with the correct subject line
    message = mailer.messages[0]
    assert message["To"] == app.config["MICROSOFT_TASK_ORDER_EMAIL_ADDRESS"]
    assert message["Subject"] == translate(
        "email.task_order_sent.subject", {"to_number": to_number}
    )

    # the email was sent as a multipart message with two parts -- the message
    # body and the attachment
    assert message.is_multipart()
    message_payload = message.get_payload()
    assert len(message_payload) == 2

    # A body and attachment were in the email
    body = next(
        (
            part
            for part in message_payload
            if part["Content-Type"] == 'text/plain; charset="utf-8"'
        ),
        None,
    )
    attachment = next(
        (part for part in message_payload if part["Content-Type"] == "application/pdf"),
        None,
    )
    assert body
    assert attachment

    assert (
        attachment["Content-Disposition"]
        == f"attachment; filename=\"{downloaded_task_order['name']}\""
    )
