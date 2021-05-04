from flask import Response

from atat.app import set_response_content_security_policy_headers


def test_response_content_security_policy_headers():
    response = Response()

    set_response_content_security_policy_headers(response, "foobar")
    assert response.headers["Content-Security-Policy"] == "foobar"
    assert response.headers["X-Content-Security-Policy"] == "foobar"
