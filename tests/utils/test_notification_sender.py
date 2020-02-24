import pytest
from unittest.mock import Mock

from tests.factories import NotificationRecipientFactory
from atat.utils.notification_sender import NotificationSender


@pytest.fixture
def notification_sender():
    return NotificationSender()


def test_can_send_notification(monkeypatch, notification_sender):
    job_mock = Mock()
    monkeypatch.setattr("atat.jobs.send_notification_mail.delay", job_mock)
    recipient_email = "test@example.com"
    email_body = "This is a test"

    NotificationRecipientFactory.create(email=recipient_email)
    notification_sender.send(email_body)

    job_mock.assert_called_once_with(
        ("test@example.com",), notification_sender.EMAIL_SUBJECT, email_body
    )
