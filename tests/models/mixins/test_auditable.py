from atat.database import db
from atat.domain.users import Users
from atat.models.mixins.auditable import AuditableMixin
from tests.factories import UserFactory


def test_logging_audit_event_on_create(mock_logger):
    user = UserFactory.create()
    assert "Audit Event create" in mock_logger.messages
    assert len(mock_logger.messages) == 1

    event_log = mock_logger.extras[0]["audit_event"]
    assert event_log["resource_type"] == "user"
    assert event_log["resource_id"] == str(user.id)
    assert event_log["display_name"] == user.full_name
    assert event_log["action"] == "create"

    assert "create" in mock_logger.extras[0]["tags"]


def test_logging_audit_event_on_delete(mock_logger):
    user = UserFactory.create()
    assert "Audit Event create" in mock_logger.messages

    db.session.delete(user)
    db.session.commit()
    assert "Audit Event delete" in mock_logger.messages
    assert len(mock_logger.messages) == 2

    event_log = mock_logger.extras[1]["audit_event"]
    assert event_log["resource_type"] == "user"
    assert event_log["resource_id"] == str(user.id)
    assert event_log["display_name"] == user.full_name
    assert event_log["action"] == "delete"

    assert "delete" in mock_logger.extras[1]["tags"]


def test_logging_audit_event_on_update(mock_logger):
    user = UserFactory.create()
    assert "Audit Event create" in mock_logger.messages

    Users.update(user, {"first_name": "Greedo"})
    assert "Audit Event update" in mock_logger.messages
    assert len(mock_logger.messages) == 2

    event_log = mock_logger.extras[1]["audit_event"]
    assert event_log["resource_type"] == "user"
    assert event_log["resource_id"] == str(user.id)
    assert event_log["display_name"] == user.full_name
    assert event_log["action"] == "update"

    assert "update" in mock_logger.extras[1]["tags"]
