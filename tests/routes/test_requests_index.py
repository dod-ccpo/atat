from flask import url_for

from atst.routes.requests.index import RequestsIndex
from tests.factories import RequestFactory, UserFactory
from atst.domain.requests import Requests


def test_action_required_mission_owner():
    creator = UserFactory.create()
    requests = RequestFactory.create_batch(5, creator=creator)
    Requests.submit(requests[0].creator, requests[0])
    context = RequestsIndex(creator).execute()

    assert context["requests"][0]["action_required"] == False


def test_action_required_ccpo():
    creator = UserFactory.create()
    requests = RequestFactory.create_batch(5, creator=creator)
    Requests.submit(requests[0].creator, requests[0])

    ccpo = UserFactory.from_atat_role("ccpo")
    context = RequestsIndex(ccpo).execute()

    assert context["num_action_required"] == 1


def test_ccpo_sees_approval_screen():
    ccpo = UserFactory.from_atat_role("ccpo")
    request = RequestFactory.create()
    Requests.submit(request.creator, request)
    ccpo_context = RequestsIndex(ccpo).execute()
    assert ccpo_context["requests"][0]["edit_link"] == url_for(
        "requests.approval", request_id=request.id
    )

    mo_context = RequestsIndex(request.creator).execute()
    assert mo_context["requests"][0]["edit_link"] != url_for(
        "requests.approval", request_id=request.id
    )
