from flask import Response
from flask import current_app as app

from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.domain.exceptions import NotFoundError
from atat.domain.task_orders import TaskOrders
from atat.models.permissions import Permissions

from .blueprint import task_orders_bp


def send_file(attachment):
    generator = app.csp.files.download(attachment.object_name)
    return Response(
        generator,
        headers={
            "Content-Disposition": "attachment; filename={}".format(attachment.filename)
        },
    )


@task_orders_bp.route("/task_orders/<task_order_id>/pdf")
@user_can(Permissions.VIEW_TASK_ORDER_DETAILS, message="download task order PDF")
def download_task_order_pdf(task_order_id):
    task_order = TaskOrders.get(task_order_id)
    if task_order.pdf:
        return send_file(task_order.pdf)
    else:
        raise NotFoundError("task_order pdf")
