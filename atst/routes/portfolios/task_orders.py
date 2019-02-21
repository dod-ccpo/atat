from collections import defaultdict

from flask import g, redirect, render_template, url_for, request as http_request

from . import portfolios_bp
from atst.database import db
from atst.domain.task_orders import TaskOrders, DD254s
from atst.domain.exceptions import NotFoundError
from atst.domain.portfolios import Portfolios
from atst.domain.authz import Authorization
from atst.forms.officers import EditTaskOrderOfficersForm
from atst.models.task_order import Status as TaskOrderStatus
from atst.forms.ko_review import KOReviewForm
from atst.forms.dd_254 import DD254Form


@portfolios_bp.route("/portfolios/<portfolio_id>/task_orders")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders_by_status = defaultdict(list)
    serialize_task_order = lambda task_order: {
        key: getattr(task_order, key)
        for key in [
            "id",
            "budget",
            "time_created",
            "start_date",
            "end_date",
            "display_status",
            "days_to_expiration",
            "balance",
        ]
    }

    for task_order in portfolio.task_orders:
        serialized_task_order = serialize_task_order(task_order)
        serialized_task_order["url"] = url_for(
            "portfolios.view_task_order",
            portfolio_id=portfolio.id,
            task_order_id=task_order.id,
        )
        task_orders_by_status[task_order.status].append(serialized_task_order)

    active_task_orders = task_orders_by_status.get(TaskOrderStatus.ACTIVE, [])
    total_balance = sum([task_order["balance"] for task_order in active_task_orders])

    return render_template(
        "portfolios/task_orders/index.html",
        portfolio=portfolio,
        pending_task_orders=(
            task_orders_by_status.get(TaskOrderStatus.STARTED, [])
            + task_orders_by_status.get(TaskOrderStatus.PENDING, [])
        ),
        active_task_orders=active_task_orders,
        expired_task_orders=task_orders_by_status.get(TaskOrderStatus.EXPIRED, []),
        total_balance=total_balance,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>")
def view_task_order(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    to_form_complete = TaskOrders.all_sections_complete(task_order)
    dd_254_complete = DD254s.is_complete(task_order.dd_254)
    return render_template(
        "portfolios/task_orders/show.html",
        dd_254_complete=dd_254_complete,
        is_cor=Authorization.is_cor(g.current_user, task_order),
        is_ko=Authorization.is_ko(g.current_user, task_order),
        is_so=Authorization.is_so(g.current_user, task_order),
        is_to_signed=TaskOrders.is_signed_by_ko(task_order),
        portfolio=portfolio,
        task_order=task_order,
        to_form_complete=to_form_complete,
        user=g.current_user,
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>/review")
def ko_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    portfolio = Portfolios.get(g.current_user, portfolio_id)

    Authorization.check_is_ko_or_cor(g.current_user, task_order)

    return render_template(
        "/portfolios/task_orders/review.html",
        portfolio=portfolio,
        task_order=task_order,
        form=KOReviewForm(obj=task_order),
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/review", methods=["POST"]
)
def submit_ko_review(portfolio_id, task_order_id, form=None):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form_data = {**http_request.form, **http_request.files}
    form = KOReviewForm(form_data)

    Authorization.check_is_ko_or_cor(g.current_user, task_order)

    if form.validate():
        TaskOrders.update(user=g.current_user, task_order=task_order, **form.data)
        if Authorization.is_ko(g.current_user, task_order):
            return redirect(
                url_for("task_orders.signature_requested", task_order_id=task_order_id)
            )
        else:
            return redirect(
                url_for(
                    "portfolios.view_task_order",
                    task_order_id=task_order_id,
                    portfolio_id=portfolio_id,
                )
            )
    else:
        return render_template(
            "/portfolios/task_orders/review.html",
            portfolio=Portfolios.get(g.current_user, portfolio_id),
            task_order=task_order,
            form=form,
        )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations"
)
def task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form = EditTaskOrderOfficersForm(obj=task_order)

    if TaskOrders.all_sections_complete(task_order):
        return render_template(
            "portfolios/task_orders/invitations.html",
            portfolio=portfolio,
            task_order=task_order,
            form=form,
        )
    else:
        raise NotFoundError("task_order")


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/invitations",
    methods=["POST"],
)
def edit_task_order_invitations(portfolio_id, task_order_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_order = TaskOrders.get(g.current_user, task_order_id)
    form = EditTaskOrderOfficersForm(formdata=http_request.form, obj=task_order)

    if form.validate():
        form.populate_obj(task_order)
        db.session.add(task_order)
        db.session.commit()

        return redirect(
            url_for(
                "portfolios.task_order_invitations",
                portfolio_id=portfolio.id,
                task_order_id=task_order.id,
            )
        )
    else:
        return render_template(
            "portfolios/task_orders/invitations.html",
            portfolio=portfolio,
            task_order=task_order,
            form=form,
        )


def so_review_form(task_order):
    if task_order.dd_254:
        dd_254 = task_order.dd_254
        form = DD254Form(obj=dd_254)
        form.required_distribution.data = dd_254.required_distribution
        return form
    else:
        so = task_order.officer_dictionary("security_officer")
        form_data = {
            "certifying_official": "{}, {}".format(
                so.get("last_name", ""), so.get("first_name", "")
            ),
            "co_phone": so.get("phone_number", ""),
        }
        return DD254Form(data=form_data)


@portfolios_bp.route("/portfolios/<portfolio_id>/task_order/<task_order_id>/dd254")
def so_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    Authorization.check_is_so(g.current_user, task_order)

    form = so_review_form(task_order)

    return render_template(
        "portfolios/task_orders/so_review.html",
        form=form,
        portfolio=task_order.portfolio,
        task_order=task_order,
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/task_order/<task_order_id>/dd254", methods=["POST"]
)
def submit_so_review(portfolio_id, task_order_id):
    task_order = TaskOrders.get(g.current_user, task_order_id)
    Authorization.check_is_so(g.current_user, task_order)

    form = DD254Form(http_request.form)

    if form.validate():
        TaskOrders.add_dd_254(task_order, form.data)
        # TODO: will redirect to download, sign, upload page
        return redirect(
            url_for(
                "portfolios.view_task_order",
                portfolio_id=task_order.portfolio.id,
                task_order_id=task_order.id,
            )
        )
    else:
        return render_template(
            "portfolios/task_orders/so_review.html",
            form=form,
            portfolio=task_order.portfolio,
            task_order=task_order,
        )
