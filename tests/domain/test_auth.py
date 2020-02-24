from flask import make_response, session

from atat.domain.auth import logout


def _write_session(app):
    response = make_response("")
    app.session_interface.save_session(app, session, response)
    return session


def test_logout_destroys_session(app):
    session = _write_session(app)
    key = app.config.get("SESSION_KEY_PREFIX") + session.sid
    assert app.redis.get(key)
    logout()
    assert app.redis.get(key) is None


def test_logout_logs_dod_id_for_current_user(monkeypatch, mock_logger):
    dod_id = "3434343434"
    monkeypatch.setattr("atat.domain.auth._current_dod_id", lambda: dod_id)
    logout()
    assert dod_id in mock_logger.messages[-1]


def test_logout_logs_message_for_unathenticated_user(mock_logger):
    logout()
    assert "unauthenticated" in mock_logger.messages[-1]
