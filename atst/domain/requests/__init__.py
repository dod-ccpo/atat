from atst.models.request import Request
from atst.models.request_status_event import RequestStatusEvent, RequestStatus

from atst.domain.requests.query import RequestQuery


def deep_merge(source, destination: dict):
    """
    Merge source dict into destination dict recursively.
    """

    def _deep_merge(a, b):
        for key, value in a.items():
            if isinstance(value, dict):
                node = b.setdefault(key, {})
                _deep_merge(value, node)
            else:
                b[key] = value

        return b

    return _deep_merge(source, dict(destination))


class Requests(object):
    AUTO_APPROVE_THRESHOLD = 1000000

    @classmethod
    def create(cls, creator, body):
        request = Request(creator=creator, body=body)
        request = Requests.set_status(request, RequestStatus.STARTED)
        return RequestQuery.create(request)

    @classmethod
    def exists(cls, request_id, creator):
        return RequestQuery.exists(request_id, creator)

    @classmethod
    def get(cls, request_id) -> Request:
        return RequestQuery.get(request_id)

    @classmethod
    def get_many(cls, creator=None):
        return RequestQuery.get_many(creator=creator)

    @classmethod
    def submit(cls, request):
        new_status = None
        if Requests.should_auto_approve(request):
            new_status = RequestStatus.PENDING_FINANCIAL_VERIFICATION
        else:
            new_status = RequestStatus.PENDING_CCPO_APPROVAL

        request = Requests.set_status(request, new_status)
        return RequestQuery.update(request)

    @classmethod
    def update(cls, request_id, request_delta):
        request = RequestQuery.get_with_lock(request_id)
        request.body = deep_merge(request_delta, request.body)
        return RequestQuery.update(request, update_body=True)

    @classmethod
    def set_status(cls, request: Request, status: RequestStatus):
        status_event = RequestStatusEvent(new_status=status)
        request.status_events.append(status_event)
        return request

    @classmethod
    def action_required_by(cls, request):
        return {
            RequestStatus.STARTED: "mission_owner",
            RequestStatus.PENDING_FINANCIAL_VERIFICATION: "mission_owner",
            RequestStatus.PENDING_CCPO_APPROVAL: "ccpo"
        }.get(request.status)

    @classmethod
    def should_auto_approve(cls, request):
        try:
            dollar_value = request.body["details_of_use"]["dollar_value"]
        except KeyError:
            return False

        return dollar_value < cls.AUTO_APPROVE_THRESHOLD

    @classmethod
    def should_allow_submission(cls, request):
        all_request_sections = [
            "details_of_use",
            "information_about_you",
            "primary_poc",
        ]
        existing_request_sections = request.body.keys()
        return request.status == RequestStatus.STARTED and all(
            section in existing_request_sections for section in all_request_sections
        )

    @classmethod
    def is_pending_financial_verification(cls, request):
        return request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION
