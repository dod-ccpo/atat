import json
import logging
from io import StringIO
from unittest.mock import Mock
from uuid import uuid4

import pytest

from atat.utils.logging import JsonFormatter, RequestContextFilter
from tests.factories import UserFactory


@pytest.fixture
def log_stream():
    return StringIO()


@pytest.fixture
def log_stream_content(log_stream):
    def _log_stream_content():
        log_stream.seek(0)
        return log_stream.read()

    return _log_stream_content


@pytest.fixture
def logger(log_stream):
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logHandler = logging.StreamHandler(log_stream)
    formatter = JsonFormatter()
    logHandler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addFilter(RequestContextFilter())
    logger.addHandler(logHandler)

    return logger


def test_json_formatter(logger, log_stream_content):
    logger.warning("do or do not", extra={"tags": ["wisdom", "jedi"]})

    log = json.loads(log_stream_content())

    assert log["tags"] == ["wisdom", "jedi"]
    assert log["message"] == "do or do not"
    assert log["severity"] == "WARNING"
    assert log.get("details") is None


def test_json_formatter_for_exceptions(logger, log_stream_content):
    try:
        raise Exception()
    except Exception:
        logger.exception("you found the ventilation shaft!")

    log = json.loads(log_stream_content())
    assert log["severity"] == "ERROR"
    assert log.get("details")


def test_request_context_filter(logger, log_stream_content, request_ctx, monkeypatch):
    request_uuid = str(uuid4())
    user_uuid = str(uuid4())

    user = Mock(spec=["id"])
    user.id = user_uuid
    user.dod_id = "5678901234"

    monkeypatch.setattr("atat.utils.logging.g", Mock(current_user=user))
    monkeypatch.setattr("atat.utils.logging.session", {"user_id": user_uuid})
    request_ctx.request.environ["HTTP_X_REQUEST_ID"] = request_uuid
    logger.info("this user is doing something")
    log = json.loads(log_stream_content())
    assert log["user_id"] == str(user_uuid)
    assert log["dod_edipi"] == str(user.dod_id)
    assert log["request_id"] == request_uuid
    assert log["logged_in"] == True
