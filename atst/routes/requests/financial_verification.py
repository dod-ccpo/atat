from flask import g, render_template, redirect, url_for
from flask import request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm, ExtendedFinancialForm


def task_order_data(task_order):
    data = task_order.to_dictionary()
    data["task_order_number"] = task_order.number
    data["funding_type"] = task_order.funding_type.value
    return data


def is_extended(request):
    return (
        http_request.args.get("extended")
        or request.is_pending_financial_verification_changes
    )


def financial_form(request, data):
    if is_extended(request):
        return ExtendedFinancialForm(data=data)
    else:
        return FinancialForm(data=data)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id=None):
    request = Requests.get(g.current_user, request_id)
    form_data = request.body.get("financial_verification")
    if request.task_order:
        form_data.update(task_order_data(request.task_order))

    form = financial_form(request, form_data)
    return render_template(
        "requests/financial_verification.html",
        f=form,
        request=request,
        review_comment=request.review_comment,
        extended=is_extended(request),
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification(request_id):
    user = g.current_user
    post_data = http_request.form
    existing_request = Requests.get(g.current_user, request_id)
    form = financial_form(existing_request, post_data)
    rerender_args = dict(
        request=existing_request, f=form, extended=is_extended(existing_request)
    )

    if form.validate():
        valid = form.perform_extra_validation(
            existing_request.body.get("financial_verification")
        )
        updated_request = Requests.update_financial_verification(
            user, request_id, form.data
        )
        if valid:
            submitted_request = Requests.submit_financial_verification(
                user, updated_request
            )
            if submitted_request.is_financially_verified:
                new_workspace = Requests.approve_and_create_workspace(
                    user, submitted_request
                )
                return redirect(
                    url_for(
                        "workspaces.new_project",
                        workspace_id=new_workspace.id,
                        newWorkspace=True,
                    )
                )
            else:
                return redirect(
                    url_for(
                        "requests.requests_index", pendingFinancialVerification=True
                    )
                )

        else:
            form.reset()
            return render_template(
                "requests/financial_verification.html", **rerender_args
            )

    else:
        form.reset()
        return render_template("requests/financial_verification.html", **rerender_args)
