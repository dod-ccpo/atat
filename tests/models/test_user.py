import pytest
from sqlalchemy.exc import InternalError
import pendulum

from atat.database import db
from atat.domain.users import Users
from atat.models.user import User

from tests.factories import UserFactory, ApplicationFactory, ApplicationRoleFactory


def test_profile_complete_with_all_info():
    user = UserFactory.create()
    assert user.profile_complete


@pytest.mark.parametrize("missing_field", User.REQUIRED_FIELDS)
def test_profile_complete_with_missing_info(missing_field):
    user = UserFactory.create()
    setattr(user, missing_field, None)
    assert not user.profile_complete


def test_cannot_update_dod_id(session):
    user = UserFactory.create()
    user.dod_id = "23403498202"
    session.add(user)
    with pytest.raises(InternalError):
        session.commit()


def test_deleted_application_roles_are_ignored(session):
    user = UserFactory.create()
    app = ApplicationFactory.create()
    app_role = ApplicationRoleFactory.create(user=user, application=app)
    assert len(user.application_roles) == 1

    app_role.deleted = True
    session.add(app_role)
    session.commit()

    assert len(user.application_roles) == 0


def test_does_not_log_user_update_when_updating_last_login(mock_logger):
    user = UserFactory.create()
    user.last_login = pendulum.now(tz="utc")
    db.session.add(user)
    db.session.commit()
    assert "Audit Event update" not in mock_logger.messages
