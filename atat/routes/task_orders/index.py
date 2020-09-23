from flask import current_app as app
from flask import g, redirect, render_template, url_for

from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.domain.portfolios import Portfolios
from atat.domain.task_orders import TaskOrders
from atat.forms.task_order import SignatureForm
from atat.models import Permissions

from .blueprint import task_orders_bp


@task_orders_bp.route("/task_orders/<task_order_id>")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="view task order details")
def view_task_order(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    pdf_download_url = app.csp.files.generate_download_link(
        task_order.pdf.object_name, task_order.pdf.filename
    )

    if task_order.is_draft:
        return redirect(url_for("task_orders.edit", task_order_id=task_order.id))
    else:
        signature_form = SignatureForm()
        return render_template(
            "task_orders/view.html",
            task_order=task_order,
            signature_form=signature_form,
            pdf_download_url=pdf_download_url,
        )


@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders")
@user_can(Permissions.VIEW_PORTFOLIO_FUNDING, message="view portfolio funding")
def portfolio_funding(portfolio_id):
    portfolio = Portfolios.get(g.current_user, portfolio_id)
    task_orders = TaskOrders.sort_by_status(portfolio.task_orders)
    to_count = len(portfolio.task_orders)
    # TODO: Get expended amount from the CSP
    return render_template(
        "task_orders/index.html", task_orders=task_orders, to_count=to_count
    )
