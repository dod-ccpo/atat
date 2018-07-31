import tornado.gen
from tornado.httpclient import HTTPRequest, HTTPResponse

from atst.api_client import ApiClient
from tests.factories import RequestFactory


MOCK_USER = {
    "id": "9cb348f0-8102-4962-88c4-dac8180c904c",
    "email": "fake.user@mail.com",
    "first_name": "Fake",
    "last_name": "User",
}
MOCK_REQUEST = RequestFactory.create(
    creator=MOCK_USER["id"],
    body={
        "financial_verification": {
            "pe_id": "0203752A",
        },
    }
)


class MockApiClient(ApiClient):

    def __init__(self, service):
        self.service = service

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return self._get_response("GET", path)

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return self._get_response("PUT", path)

    @tornado.gen.coroutine
    def patch(self, path, **kwargs):
        return self._get_response("PATCH", path)

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return self._get_response("POST", path)

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return self._get_response("DELETE", path)

    def _get_response(self, verb, path, code=200, json=None):
        response = HTTPResponse(
            request=HTTPRequest(path, verb),
            code=code,
            headers={"Content-Type": "application/json"},
        )

        setattr(response, "ok", 200 <= code < 300)
        if json:
            setattr(response, "json", json)

        return response


MOCK_VALID_PE_ID = "8675309U"

class MockFundzClient(MockApiClient):

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        if path.endswith(MOCK_VALID_PE_ID):
            return self._get_response("GET", path, 200)
        else:
            return self._get_response("GET", path, 404)


class MockAuthzClient(MockApiClient):
    _json = {
        "atat_permissions": [
            "view_original_jedi_request",
            "review_and_approve_jedi_workspace_request",
            "modify_atat_role_permissions",
            "create_csp_role",
            "delete_csp_role",
            "deactivate_csp_role",
            "modify_csp_role_permissions",
            "view_usage_report",
            "view_usage_dollars",
            "add_and_assign_csp_roles",
            "remove_csp_roles",
            "request_new_csp_role",
            "assign_and_unassign_atat_role",
            "view_assigned_atat_role_configurations",
            "view_assigned_csp_role_configurations",
            "deactivate_workspace",
            "view_atat_permissions",
            "transfer_ownership_of_workspace",
            "add_application_in_workspace",
            "delete_application_in_workspace",
            "deactivate_application_in_workspace",
            "view_application_in_workspace",
            "rename_application_in_workspace",
            "add_environment_in_application",
            "delete_environment_in_application",
            "deactivate_environment_in_application",
            "view_environment_in_application",
            "rename_environment_in_application",
            "add_tag_to_workspace",
            "remove_tag_from_workspace",
        ],
        "atat_role": "ccpo",
        "id": "164497f6-c1ea-4f42-a5ef-101da278c012",
        "username": None,
        "workspace_roles": [],
    }

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return self._get_response("POST", path, 200, json=self._json)

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return self._get_response("POST", path, 200, json=self._json)
