from flask import g, redirect, render_template, url_for, request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.routes.requests.jedi_request_flow import JEDIRequestFlow
from atst.models.request_status_event import RequestStatus
from atst.forms.data import (
    SERVICE_BRANCHES,
    ASSISTANCE_ORG_TYPES,
    DATA_TRANSFER_AMOUNTS,
    COMPLETION_DATE_RANGES,
    FUNDING_TYPES,
    TASK_ORDER_SOURCES,
)


@requests_bp.context_processor
def option_data():
    return {
        "service_branches": SERVICE_BRANCHES,
        "assistance_org_types": ASSISTANCE_ORG_TYPES,
        "data_transfer_amounts": DATA_TRANSFER_AMOUNTS,
        "completion_date_ranges": COMPLETION_DATE_RANGES,
        "funding_types": FUNDING_TYPES,
        "task_order_sources": TASK_ORDER_SOURCES,
    }


@requests_bp.route("/requests/new/<int:screen>", methods=["GET"])
def requests_form_new(screen):
    jedi_flow = JEDIRequestFlow(screen, request=None, current_user=g.current_user)

    return render_template(
        "requests/screen-%d.html" % int(screen),
        f=jedi_flow.form,
        data=jedi_flow.current_step_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=screen + 1,
        can_submit=jedi_flow.can_submit,
    )


@requests_bp.route(
    "/requests/new/<int:screen>", methods=["GET"], defaults={"request_id": None}
)
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["GET"])
def requests_form_update(screen=1, request_id=None):
    request = (
        Requests.get(g.current_user, request_id) if request_id is not None else None
    )
    jedi_flow = JEDIRequestFlow(
        screen, request=request, request_id=request_id, current_user=g.current_user
    )

    return render_template(
        "requests/screen-%d.html" % int(screen),
        f=jedi_flow.form,
        data=jedi_flow.current_step_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=screen + 1,
        request_id=request_id,
        jedi_request=jedi_flow.request,
        review_comment=request.review_comment,
        can_submit=jedi_flow.can_submit,
    )


@requests_bp.route(
    "/requests/new/<int:screen>", methods=["POST"], defaults={"request_id": None}
)
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["POST"])
def requests_update(screen=1, request_id=None):
    screen = int(screen)
    post_data = http_request.form
    current_user = g.current_user
    existing_request = (
        Requests.get(g.current_user, request_id) if request_id is not None else None
    )
    jedi_flow = JEDIRequestFlow(
        screen,
        post_data=post_data,
        request_id=request_id,
        current_user=current_user,
        existing_request=existing_request,
    )

    has_next_screen = jedi_flow.next_screen <= len(jedi_flow.screens)
    valid = jedi_flow.validate() and jedi_flow.validate_warnings()

    if valid:
        jedi_flow.create_or_update_request()

        if has_next_screen:
            where = url_for(
                "requests.requests_form_update",
                screen=jedi_flow.next_screen,
                request_id=jedi_flow.request_id,
            )
        else:
            where = "/requests"
        return redirect(where)
    else:
        rerender_args = dict(
            f=jedi_flow.form,
            data=post_data,
            screens=jedi_flow.screens,
            current=screen,
            next_screen=jedi_flow.next_screen,
            request_id=jedi_flow.request_id,
        )
        return render_template("requests/screen-%d.html" % int(screen), **rerender_args)


@requests_bp.route("/requests/submit/<string:request_id>", methods=["POST"])
def requests_submit(request_id=None):
    request = Requests.get(g.current_user, request_id)
    Requests.submit(g.current_user, request)

    if request.status == RequestStatus.PENDING_FINANCIAL_VERIFICATION:
        return redirect("/requests?modal=pendingFinancialVerification")

    else:
        return redirect("/requests?modal=pendingCCPOApproval")


@requests_bp.route("/requests/details/<string:request_id>", methods=["GET"])
def view_request_details(request_id=None):
    request = Requests.get(g.current_user, request_id)
    requires_fv_action = (
        request.is_pending_financial_verification
        or request.is_pending_financial_verification_changes
    )

    data = request.body
    if request.has_financial_data:
        data["task_order"] = request.task_order.to_dictionary()

    return render_template(
        "requests/details.html",
        data=data,
        request=request,
        requires_fv_action=requires_fv_action,
    )
