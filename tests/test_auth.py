import os
from urllib.parse import urlparse

import pytest
from datetime import datetime
import pendulum
from flask import session, url_for
from cryptography.hazmat.primitives.serialization import Encoding

from atat.domain.users import Users
from atat.domain.exceptions import NotFoundError
from atat.domain.authnid.crl import CRLInvalidException
from atat.domain.auth import UNPROTECTED_ROUTES
from atat.domain.authnid.crl import CRLCache

from .factories import UserFactory
from .mocks import DOD_SDN_INFO, DOD_SDN, FIXTURE_EMAIL_ADDRESS
from .utils import make_crl_list, FakeLogger


MOCK_USER = {"id": "438567dd-25fa-4d83-a8cc-8aa8366cb24a"}


def _fetch_user_info(c, t):
    return MOCK_USER


def _login(client, verify="SUCCESS", sdn=DOD_SDN, cert="", **url_query_args):
    return client.get(
        url_for("atat.login_redirect", **url_query_args),
        environ_base={
            "HTTP_X_SSL_CLIENT_VERIFY": verify,
            "HTTP_X_SSL_CLIENT_S_DN": sdn,
            "HTTP_X_SSL_CLIENT_CERT": cert,
        },
    )


def test_successful_login_redirect(client, monkeypatch, mock_logger):
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda *args: True
    )
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.get_user",
        lambda *args: UserFactory.create(),
    )

    resp = _login(client)

    assert resp.status_code == 302
    assert "home" in resp.headers["Location"]
    assert session["user_id"]

    login_msg = mock_logger.messages[-1]
    assert "succeeded" in login_msg


def test_unsuccessful_login_redirect(client, monkeypatch, mock_logger):
    resp = client.get(url_for("atat.login_redirect"))

    assert resp.status_code == 401
    assert "user_id" not in session

    login_msg = mock_logger.messages[0]
    assert "failed" in login_msg


# checks that all of the routes in the app are protected by auth
def is_unprotected(rule):
    return rule.endpoint in UNPROTECTED_ROUTES


def protected_routes(app):
    for rule in app.url_map.iter_rules():
        args = [1] * len(rule.arguments)
        mock_args = dict(zip(rule.arguments, args))
        _n, route = rule.build(mock_args)
        if is_unprotected(rule) or "/static" in route:
            continue
        yield rule, route


def test_protected_routes_redirect_to_login(client, app):
    server_name = app.config.get("SERVER_NAME") or "localhost"
    for rule, protected_route in protected_routes(app):
        if "GET" in rule.methods:
            resp = client.get(protected_route)
            assert resp.status_code == 302
            assert server_name in resp.headers["Location"]

        if "POST" in rule.methods:
            resp = client.post(protected_route)
            assert resp.status_code == 302
            assert server_name in resp.headers["Location"]


def test_unprotected_routes_set_user_if_logged_in(client, app, user_session):
    user = UserFactory.create()

    resp = client.get(url_for("atat.about"))
    assert resp.status_code == 200
    assert user.full_name not in resp.data.decode()

    user_session(user)
    resp = client.get(url_for("atat.about"))
    assert resp.status_code == 200
    assert user.full_name in resp.data.decode()


@pytest.fixture
def swap_crl_cache(
    app, ca_key, ca_file, crl_file, make_crl, serialize_pki_object_to_disk
):
    original = app.crl_cache

    def _swap_crl_cache(new_cache=None):
        if new_cache:
            app.crl_cache = new_cache
        else:
            crl = make_crl(ca_key)
            serialize_pki_object_to_disk(crl, crl_file, encoding=Encoding.DER)
            crl_dir = os.path.dirname(crl_file)
            crl_list = make_crl_list(crl, crl_file)
            app.crl_cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)

    yield _swap_crl_cache

    app.crl_cache = original


def test_crl_validation_on_login(
    app,
    client,
    ca_key,
    ca_file,
    crl_file,
    rsa_key,
    make_x509,
    make_crl,
    serialize_pki_object_to_disk,
    swap_crl_cache,
):
    good_cert = make_x509(rsa_key(), signer_key=ca_key, cn="luke")
    bad_cert = make_x509(rsa_key(), signer_key=ca_key, cn="darth")

    crl = make_crl(ca_key, expired_serials=[bad_cert.serial_number])
    serialize_pki_object_to_disk(crl, crl_file, encoding=Encoding.DER)

    crl_dir = os.path.dirname(crl_file)
    crl_list = make_crl_list(good_cert, crl_file)
    cache = CRLCache(ca_file, crl_dir, crl_list=crl_list)
    swap_crl_cache(cache)

    # bad cert is on the test CRL
    resp = _login(client, cert=bad_cert.public_bytes(Encoding.PEM).decode())
    assert resp.status_code == 401
    assert "user_id" not in session

    # good cert is not on the test CRL, passes
    resp = _login(client, cert=good_cert.public_bytes(Encoding.PEM).decode())
    assert session["user_id"]


def test_creates_new_user_on_login(monkeypatch, client, ca_key):
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda *args: True
    )
    cert_file = open("tests/fixtures/{}.crt".format(FIXTURE_EMAIL_ADDRESS)).read()

    # ensure user does not exist
    with pytest.raises(NotFoundError):
        Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])

    resp = _login(client, cert=cert_file)

    user = Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])
    assert user.first_name == DOD_SDN_INFO["first_name"]
    assert user.last_name == DOD_SDN_INFO["last_name"]
    assert user.email == FIXTURE_EMAIL_ADDRESS


def test_creates_new_user_without_email_on_login(
    client, ca_key, rsa_key, make_x509, swap_crl_cache
):
    cert = make_x509(rsa_key(), signer_key=ca_key, cn=DOD_SDN)
    swap_crl_cache()

    # ensure user does not exist
    with pytest.raises(NotFoundError):
        Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])

    resp = _login(client, cert=cert.public_bytes(Encoding.PEM).decode())

    user = Users.get_by_dod_id(DOD_SDN_INFO["dod_id"])
    assert user.first_name == DOD_SDN_INFO["first_name"]
    assert user.last_name == DOD_SDN_INFO["last_name"]
    assert user.email == None


def test_logout(app, client, monkeypatch, mock_logger):
    user = UserFactory.create()
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda s: True
    )
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.get_user", lambda s: user,
    )
    # create a real session
    resp = _login(client)
    resp_success = client.get(url_for("users.user"))
    # verify session is valid
    assert resp_success.status_code == 200
    client.get(url_for("atat.logout"))
    resp_failure = client.get(url_for("users.user"))
    # verify that logging out has cleared the session
    assert resp_failure.status_code == 302
    destination = urlparse(resp_failure.headers["Location"]).path
    assert destination == url_for("atat.root")
    # verify that logout is noted in the logs
    logout_msg = mock_logger.messages[-1]
    assert user.dod_id in logout_msg
    assert "logged out" in logout_msg


def test_logging_out_creates_a_flash_message(app, client, monkeypatch):
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda s: True
    )
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.get_user",
        lambda s: UserFactory.create(),
    )
    _login(client)
    logout_response = client.get(url_for("atat.logout"), follow_redirects=True)

    assert "Logged out" in logout_response.data.decode()


def test_redirected_on_login(client, monkeypatch):
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda *args: True
    )
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.get_user",
        lambda *args: UserFactory.create(),
    )
    target_route = url_for("users.user")
    response = _login(client, next=target_route)
    assert target_route in response.headers.get("Location")


def test_error_on_invalid_crl(client, monkeypatch):
    def _raise_crl_error(*args):
        raise CRLInvalidException()

    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", _raise_crl_error
    )
    response = _login(client)
    assert response.status_code == 401
    assert "Error Code 008" in response.data.decode()


def test_last_login_set_when_user_logs_in(client, monkeypatch):
    last_login = pendulum.now(tz="utc")
    user = UserFactory.create(last_login=last_login)
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.authenticate", lambda *args: True
    )
    monkeypatch.setattr(
        "atat.domain.authnid.AuthenticationContext.get_user", lambda *args: user
    )
    _login(client)
    assert session["last_login"]
    assert user.last_login > session["last_login"]
    assert isinstance(session["last_login"], datetime)
