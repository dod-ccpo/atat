from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import requests

from atat.domain.csp.cloud.models import UserCSPPayload
from atat.domain.csp.cloud.utils import (
    create_active_directory_user,
    get_principal_auth_token,
    make_auth_header,
)
from tests.domain.cloud.test_azure_csp import mock_requests_response
from tests.mock_azure import mock_requests


@patch("atat.domain.csp.cloud.utils.requests", new_callable=mock_requests)
def test_get_principal_auth_token(mock_requests):
    mock_requests.post.side_effect = [
        mock_requests_response(
            status=500,
            raise_for_status=requests.exceptions.HTTPError("500 Server Error"),
        ),
        mock_requests_response(json_data={"access_token": "token"}),
        mock_requests_response(json_data={}),
    ]
    payload = MagicMock(return_value={})

    with pytest.raises(requests.HTTPError):
        get_principal_auth_token("a_tenant_id", payload)

    assert get_principal_auth_token("a_tenant_id", payload) == "token"
    assert get_principal_auth_token("a_tenant_id", payload) is None


def test_make_auth_header():
    header = make_auth_header("foo")
    assert header["Authorization"] == "Bearer foo"


@patch("atat.domain.csp.cloud.utils.requests", new_callable=mock_requests)
def test_create_active_directory_user(mock_requests):
    mock_result = mock_requests_response(json_data={"id": "id"})

    mock_requests.post.side_effect = [
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
        mock_result,
    ]

    payload = UserCSPPayload(
        tenant_id=uuid4().hex,
        display_name="Test Testerson",
        tenant_host_name="testtenant",
        email="test@testerson.test",
        password="asdfghjkl",  # pragma: allowlist secret
    )
    with pytest.raises(requests.exceptions.ConnectionError):
        create_active_directory_user("token", "azure.com", payload)
    with pytest.raises(requests.exceptions.Timeout):
        create_active_directory_user("token", "azure.com", payload)
    with pytest.raises(requests.exceptions.HTTPError):
        create_active_directory_user("token", "azure.com", payload)

    result = create_active_directory_user("token", "azure.com", payload)

    assert result == mock_result
