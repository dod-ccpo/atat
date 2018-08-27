from enum import Enum
from sqlalchemy import exists, and_, exc
from sqlalchemy.sql import text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.attributes import flag_modified

from atst.models.request import Request
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.domain.workspaces import Workspaces
from atst.database import db
from atst.domain.task_orders import TaskOrders

from .exceptions import NotFoundError


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
    ANNUAL_SPEND_THRESHOLD = 1000000

    @classmethod
    def create(cls, creator, body):
        request = Request(creator=creator, body=body)
        request = Requests.set_status(request, RequestStatus.STARTED)

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def exists(cls, request_id, creator):
        try:
            return db.session.query(
                exists().where(
                    and_(Request.id == request_id, Request.creator == creator)
                )
            ).scalar()

        except exc.DataError:
            return False

    @classmethod
    def get(cls, request_id):
        try:
            request = db.session.query(Request).filter_by(id=request_id).one()
        except NoResultFound:
            raise NotFoundError("request")

        return request

    @classmethod
    def get_many(cls, creator=None):
        filters = []
        if creator:
            filters.append(Request.creator == creator)

        requests = (
            db.session.query(Request)
            .filter(*filters)
            .order_by(Request.time_created.desc())
            .all()
        )
        return requests

    @classmethod
    def submit(cls, request):
        new_status = None
        if Requests.should_auto_approve(request):
            new_status = RequestStatus.PENDING_FINANCIAL_VERIFICATION
        else:
            new_status = RequestStatus.PENDING_CCPO_APPROVAL

        request = Requests.set_status(request, new_status)

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def update(cls, request_id, request_delta):
        request = Requests._get_with_lock(request_id)
        if not request:
            return

        request = Requests._merge_body(request, request_delta)

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def _get_with_lock(cls, request_id):
        try:
            # Query for request matching id, acquiring a row-level write lock.
            # https://www.postgresql.org/docs/10/static/sql-select.html#SQL-FOR-UPDATE-SHARE
            return (
                db.session.query(Request)
                .filter_by(id=request_id)
                .with_for_update(of=Request)
                .one()
            )

        except NoResultFound:
            return

    @classmethod
    def _merge_body(cls, request, request_delta):
        request.body = deep_merge(request_delta, request.body)

        # Without this, sqlalchemy won't notice the change to request.body,
        # since it doesn't track dictionary mutations by default.
        flag_modified(request, "body")

        return request

    @classmethod
    def approve_and_create_workspace(cls, request):
        approved_request = Requests.set_status(request, RequestStatus.APPROVED)
        workspace = Workspaces.create(approved_request)

        db.session.add(approved_request)
        db.session.commit()

        return workspace

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
            RequestStatus.PENDING_CCPO_APPROVAL: "ccpo",
        }.get(request.status)

    @classmethod
    def should_auto_approve(cls, request):
        try:
            dollar_value = request.body["details_of_use"]["dollar_value"]
        except KeyError:
            return False

        return dollar_value < cls.AUTO_APPROVE_THRESHOLD

    _VALID_SUBMISSION_STATUSES = [
        RequestStatus.STARTED,
        RequestStatus.CHANGES_REQUESTED,
    ]

    @classmethod
    def should_allow_submission(cls, request):
        all_request_sections = [
            "details_of_use",
            "information_about_you",
            "primary_poc",
        ]
        existing_request_sections = request.body.keys()
        return request.status in Requests._VALID_SUBMISSION_STATUSES and all(
            section in existing_request_sections for section in all_request_sections
        )

    @classmethod
    def is_pending_financial_verification(cls, request):
        return request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION

    @classmethod
    def is_pending_ccpo_approval(cls, request):
        return request.status == RequestStatus.PENDING_CCPO_APPROVAL

    @classmethod
    def status_count(cls, status, creator=None):
        if isinstance(status, Enum):
            status = status.name
        bindings = {"status": status}
        raw = """
SELECT count(requests_with_status.id)
FROM (
    SELECT DISTINCT ON (rse.request_id) r.*, rse.new_status as status
    FROM request_status_events rse JOIN requests r ON r.id = rse.request_id
    ORDER BY rse.request_id, rse.sequence DESC
) as requests_with_status
WHERE requests_with_status.status = :status
        """

        if creator:
            raw += " AND requests_with_status.user_id = :user_id"
            bindings["user_id"] = creator.id

        results = db.session.execute(text(raw), bindings).fetchone()
        (count,) = results
        return count

    @classmethod
    def in_progress_count(cls):
        return sum(
            [
                Requests.status_count(RequestStatus.STARTED),
                Requests.status_count(RequestStatus.PENDING_FINANCIAL_VERIFICATION),
                Requests.status_count(RequestStatus.CHANGES_REQUESTED),
            ]
        )

    @classmethod
    def pending_ccpo_count(cls):
        return Requests.status_count(RequestStatus.PENDING_CCPO_APPROVAL)

    @classmethod
    def completed_count(cls):
        return Requests.status_count(RequestStatus.APPROVED)

    @classmethod
    def update_financial_verification(cls, request_id, financial_data):
        request = Requests._get_with_lock(request_id)
        if not request:
            return

        request_data = financial_data.copy()
        task_order_data = {
            k: request_data.pop(k)
            for (k, v) in financial_data.items()
            if k in TaskOrders.TASK_ORDER_DATA
        }
        if task_order_data:
            task_order_number = request_data.pop("task_order_number")
        else:
            task_order_number = request_data.get("task_order_number")

        task_order = TaskOrders.get_or_create_task_order(
            task_order_number, task_order_data
        )

        if task_order:
            request.task_order = task_order

        request = Requests._merge_body(
            request, {"financial_verification": request_data}
        )

        db.session.add(request)
        db.session.commit()

        return request

    @classmethod
    def submit_financial_verification(cls, request_id):
        request = Requests._get_with_lock(request_id)
        if not request:
            return

        Requests.set_status(request, RequestStatus.PENDING_CCPO_APPROVAL)

        db.session.add(request)
        db.session.commit()
