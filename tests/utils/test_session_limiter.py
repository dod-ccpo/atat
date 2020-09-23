from unittest.mock import Mock
from uuid import uuid4

import pytest
from redis import Redis

from atat.models.user import User
from atat.utils.session_limiter import SessionLimiter
from tests.factories import UserFactory


@pytest.fixture
def mock_redis():
    return Mock(spec=Redis)


@pytest.fixture
def mock_session():
    mock = Mock(spec=["sid"])
    mock.sid = uuid4()
    return mock


def test_session_limiter_deletes_users_old_session(mock_redis, mock_session):
    last_session_id = uuid4()
    current_session_id = uuid4()

    mock_session.sid = current_session_id

    session_limiter = SessionLimiter(
        {"LIMIT_CONCURRENT_SESSIONS": True}, mock_session, mock_redis
    )
    user = UserFactory.create(last_session_id=last_session_id)
    session_limiter.on_login(user)

    mock_redis.delete.assert_called_with("session:{}".format(last_session_id))


def test_session_limiter_updates_users_last_sesion_id(mock_redis, mock_session, db):
    last_session_id = uuid4()
    current_session_id = uuid4()

    mock_session.sid = current_session_id

    session_limiter = SessionLimiter(
        {"LIMIT_CONCURRENT_SESSIONS": True}, mock_session, mock_redis
    )
    user = UserFactory.create(last_session_id=last_session_id)
    session_limiter.on_login(user)

    user = db.session.query(User).get(user.id)
    assert user.last_session_id == current_session_id
