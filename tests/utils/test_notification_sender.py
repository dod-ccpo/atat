import pytest
from unittest.mock import Mock

from tests.factories import NotificationRecipientFactory
from atst.utils.notification_sender import NotificationSender


@pytest.fixture
def mock_queue(queue):
    return Mock(spec=queue)


@pytest.fixture
def notification_sender(mock_queue, mock_logger):
    return NotificationSender(mock_queue, mock_logger)


def test_can_send_notification(mock_queue, notification_sender):
    recipient_email = "test@example.com"
    email_body = "This is a test"

    NotificationRecipientFactory.create(email=recipient_email)
    notification_sender.send(email_body)

    mock_queue.send_notification_mail.assert_called_once_with(
        ("test@example.com",), notification_sender.EMAIL_SUBJECT, email_body
    )
