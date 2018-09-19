import pytest
from uuid import uuid4

from atst.domain.exceptions import NotFoundError
from atst.domain.requests import Requests
from atst.models.request import Request
from atst.models.request_status_event import RequestStatus
from atst.models.task_order import Source as TaskOrderSource

from tests.factories import (
    RequestFactory,
    UserFactory,
    RequestStatusEventFactory,
    TaskOrderFactory,
    RequestRevisionFactory,
    RequestReviewFactory,
)


@pytest.fixture(scope="function")
def new_request(session):
    return RequestFactory.create()


def test_can_get_request():
    factory_req = RequestFactory.create()
    request = Requests.get(factory_req.creator, factory_req.id)

    assert request.id == factory_req.id


def test_nonexistent_request_raises():
    a_user = UserFactory.build()
    with pytest.raises(NotFoundError):
        Requests.get(a_user, uuid4())


def test_new_request_has_started_status():
    request = Requests.create(UserFactory.build(), {})
    assert request.status == RequestStatus.STARTED


def test_auto_approve_less_than_1m():
    new_request = RequestFactory.create(initial_revision={"dollar_value": 999999})
    request = Requests.submit(new_request.creator, new_request)

    assert request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION


def test_dont_auto_approve_if_dollar_value_is_1m_or_above():
    new_request = RequestFactory.create(initial_revision={"dollar_value": 1000000})
    request = Requests.submit(new_request.creator, new_request)

    assert request.status == RequestStatus.PENDING_CCPO_ACCEPTANCE


def test_dont_auto_approve_if_no_dollar_value_specified():
    new_request = RequestFactory.create(initial_revision={})
    request = Requests.submit(new_request.creator, new_request)

    assert request.status == RequestStatus.PENDING_CCPO_ACCEPTANCE


def test_should_allow_submission():
    new_request = RequestFactory.create()

    assert Requests.should_allow_submission(new_request)

    RequestStatusEventFactory.create(
        request=new_request,
        new_status=RequestStatus.CHANGES_REQUESTED,
        revision=new_request.latest_revision,
    )
    assert Requests.should_allow_submission(new_request)

    # new, blank revision
    RequestRevisionFactory.create(request=new_request)
    assert not Requests.should_allow_submission(new_request)


def test_request_knows_its_last_submission_timestamp(new_request):
    submitted_request = Requests.submit(new_request.creator, new_request)
    assert submitted_request.last_submission_timestamp


def test_request_knows_if_it_has_no_last_submission_timestamp(new_request):
    assert new_request.last_submission_timestamp is None


def test_exists(session):
    user_allowed = UserFactory.create()
    user_denied = UserFactory.create()
    request = RequestFactory.create(creator=user_allowed)
    assert Requests.exists(request.id, user_allowed)
    assert not Requests.exists(request.id, user_denied)


def test_status_count(session):
    # make sure table is empty
    session.query(Request).delete()

    request1 = RequestFactory.create()
    request2 = RequestFactory.create()
    RequestStatusEventFactory.create(
        sequence=2,
        request_id=request2.id,
        revision=request2.latest_revision,
        new_status=RequestStatus.PENDING_FINANCIAL_VERIFICATION,
    )

    assert Requests.status_count(RequestStatus.PENDING_FINANCIAL_VERIFICATION) == 1
    assert Requests.status_count(RequestStatus.STARTED) == 1
    assert Requests.in_progress_count() == 2


def test_status_count_scoped_to_creator(session):
    # make sure table is empty
    session.query(Request).delete()

    user = UserFactory.create()
    request1 = RequestFactory.create()
    request2 = RequestFactory.create(creator=user)

    assert Requests.status_count(RequestStatus.STARTED) == 2
    assert Requests.status_count(RequestStatus.STARTED, creator=user) == 1


request_financial_data = {
    "pe_id": "123",
    "task_order_number": "021345",
    "fname_co": "Contracting",
    "lname_co": "Officer",
    "email_co": "jane@mail.mil",
    "office_co": "WHS",
    "fname_cor": "Officer",
    "lname_cor": "Representative",
    "email_cor": "jane@mail.mil",
    "office_cor": "WHS",
    "uii_ids": "1234",
    "treasury_code": "00123456",
    "ba_code": "024A",
}


def test_update_financial_verification_without_task_order(
    extended_financial_verification_data
):
    request = RequestFactory.create()
    financial_data = {**request_financial_data, **extended_financial_verification_data}
    Requests.update_financial_verification(request.creator, request.id, financial_data)
    assert request.task_order
    assert request.task_order.clin_0001 == int(
        extended_financial_verification_data["clin_0001"]
    )
    assert request.task_order.source == TaskOrderSource.MANUAL
    assert request.task_order.pdf


def test_update_financial_verification_with_task_order():
    task_order = TaskOrderFactory.create(source=TaskOrderSource.EDA)
    financial_data = {**request_financial_data, "task_order_number": task_order.number}
    request = RequestFactory.create()
    Requests.update_financial_verification(request.creator, request.id, financial_data)
    assert request.task_order == task_order


def test_update_financial_verification_with_invalid_task_order():
    request = RequestFactory.create()
    Requests.update_financial_verification(
        request.creator, request.id, request_financial_data
    )
    assert not request.task_order
    assert "task_order_number" in request.body.get("financial_verification")
    assert (
        request.body["financial_verification"]["task_order_number"]
        == request_financial_data["task_order_number"]
    )


def test_set_status_sets_revision():
    request = RequestFactory.create()
    Requests.set_status(request.creator, request, RequestStatus.APPROVED)
    assert request.latest_revision == request.status_events[-1].revision


def test_advance_to_financial_verification():
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    review_data = RequestReviewFactory.dictionary()
    Requests.advance(UserFactory.create(), request, review_data)
    assert request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION
    current_review = request.latest_status.review
    assert current_review.fname_mao == review_data["fname_mao"]


def test_advance_to_approval():
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_APPROVAL
    )
    review_data = RequestReviewFactory.dictionary()
    Requests.advance(UserFactory.create(), request, review_data)
    assert request.status == RequestStatus.APPROVED


def test_request_changes_to_request_application():
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_ACCEPTANCE
    )
    review_data = RequestReviewFactory.dictionary()
    Requests.request_changes(UserFactory.create(), request, review_data)
    assert request.status == RequestStatus.CHANGES_REQUESTED
    current_review = request.latest_status.review
    assert current_review.fname_mao == review_data["fname_mao"]


def test_request_changes_to_financial_verification_info():
    request = RequestFactory.create_with_status(
        status=RequestStatus.PENDING_CCPO_APPROVAL
    )
    review_data = RequestReviewFactory.dictionary()
    Requests.request_changes(UserFactory.create(), request, review_data)
    assert request.status == RequestStatus.CHANGES_REQUESTED_TO_FINVER
    current_review = request.latest_status.review
    assert current_review.fname_mao == review_data["fname_mao"]


def test_update_internal_comments():
    request = RequestFactory.create()
    ccpo = UserFactory.from_atat_role("ccpo")

    request = Requests.update_internal_comments(ccpo, request, "this is my comment")

    assert request.internal_comments.text == "this is my comment"
