from flask import render_template

from . import task_orders_bp
import atst.forms.task_order as task_order_form


class TaskOrderSignatureWorkflow:
    def __init__(self):
        self._form = task_order_form.SignatureForm()

    @property
    def form(self):
        return self._form


@task_orders_bp.route("/task_orders/<task_order_id>/sign", methods=["GET"])
def show_signature(task_order_id=None):
    workflow = TaskOrderSignatureWorkflow()

    return render_template(
        "/task_orders/sign/show.html", task_order_id=task_order_id, form=workflow.form
    )
