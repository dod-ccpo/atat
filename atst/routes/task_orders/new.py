from copy import deepcopy

from flask import (
    request as http_request,
    render_template,
    g,
    redirect,
    url_for,
    current_app as app,
)

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.portfolios import Portfolios
from atst.domain.portfolio_roles import PortfolioRoles
import atst.forms.task_order as task_order_form
from atst.services.invitation import Invitation as InvitationService


TASK_ORDER_SECTIONS = [
    {
        "section": "app_info",
        "title": "What You're Making",
        "template": "task_orders/new/app_info.html",
        "form": task_order_form.AppInfoForm,
    },
    {
        "section": "funding",
        "title": "Funding",
        "template": "task_orders/new/funding.html",
        "form": task_order_form.FundingForm,
        "unclassified_form": task_order_form.UnclassifiedFundingForm,
    },
    {
        "section": "oversight",
        "title": "Oversight",
        "template": "task_orders/new/oversight.html",
        "form": task_order_form.OversightForm,
    },
    {
        "section": "review",
        "title": "Review & Download",
        "template": "task_orders/new/review.html",
        "form": task_order_form.ReviewForm,
    },
]


class ShowTaskOrderWorkflow:
    def __init__(self, user, screen=1, task_order_id=None):
        self.user = user
        self.screen = screen
        self.task_order_id = task_order_id
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._task_order = None
        self._form = None

    @property
    def task_order(self):
        if not self._task_order and self.task_order_id:
            self._task_order = TaskOrders.get(self.user, self.task_order_id)

        return self._task_order

    @property
    def form(self):
        form_type = (
            "unclassified_form"
            if "unclassified_form" in self._section and not app.config.get("CLASSIFIED")
            else "form"
        )

        if self._form:
            pass
        elif self.task_order:
            self._form = self._section[form_type](obj=self.task_order)
            # manually set SelectMultipleFields
            if self._section["section"] == "app_info":
                self._form.complexity.data = self.task_order.complexity
                self._form.dev_team.data = self.task_order.dev_team
            elif self._section["section"] == "oversight":
                if self.user.dod_id == self.task_order.cor_dod_id:
                    self._form.am_cor.data = True

        else:
            self._form = self._section[form_type]()

        return self._form

    @property
    def template(self):
        return self._section["template"]

    @property
    def display_screens(self):
        screen_info = deepcopy(TASK_ORDER_SECTIONS)

        if self.task_order:
            for section in screen_info:
                section["complete"] = TaskOrders.section_completion_status(
                    self.task_order, section["section"]
                )

        return screen_info


class UpdateTaskOrderWorkflow(ShowTaskOrderWorkflow):
    def __init__(
        self, user, form_data, screen=1, task_order_id=None, portfolio_id=None
    ):
        self.user = user
        self.form_data = form_data
        self.screen = screen
        self.task_order_id = task_order_id
        self.portfolio_id = portfolio_id
        self._task_order = None
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._form = self._section["form"](self.form_data)

    @property
    def form(self):
        return self._form

    @property
    def portfolio(self):
        if self.task_order:
            return self.task_order.portfolio

    @property
    def task_order_form_data(self):
        to_data = self.form.data.copy()
        if "portfolio_name" in to_data:
            to_data.pop("portfolio_name")

        # don't save other text in DB unless "other" is checked
        if "complexity" in to_data and "other" not in to_data["complexity"]:
            to_data["complexity_other"] = None
        if "dev_team" in to_data and "other" not in to_data["dev_team"]:
            to_data["dev_team_other"] = None

        if self.form_data.get("am_cor"):
            cor_data = {
                "cor_first_name": self.user.first_name,
                "cor_last_name": self.user.last_name,
                "cor_email": self.user.email,
                "cor_phone_number": self.user.phone_number,
                "cor_dod_id": self.user.dod_id,
            }
            to_data = {**to_data, **cor_data}

        return to_data

    def validate(self):
        return self.form.validate()

    def _update_task_order(self):
        if self.task_order:
            if "portfolio_name" in self.form.data:
                new_name = self.form.data["portfolio_name"]
                old_name = self.task_order.portfolio_name
                if not new_name == old_name:
                    Portfolios.update(self.task_order.portfolio, {"name": new_name})
            TaskOrders.update(self.user, self.task_order, **self.task_order_form_data)
        else:
            if self.portfolio_id:
                pf = Portfolios.get(self.user, self.portfolio_id)
            else:
                pf = Portfolios.create(self.user, self.form.portfolio_name.data)
            self._task_order = TaskOrders.create(portfolio=pf, creator=self.user)
            TaskOrders.update(self.user, self.task_order, **self.task_order_form_data)

    OFFICER_INVITATIONS = [
        {
            "field": "ko_invite",
            "prefix": "ko",
            "role": "contracting_officer",
            "subject": "Review a task order",
            "template": "emails/invitation.txt",
        },
        {
            "field": "cor_invite",
            "prefix": "cor",
            "role": "contracting_officer_representative",
            "subject": "Help with a task order",
            "template": "emails/invitation.txt",
        },
        {
            "field": "so_invite",
            "prefix": "so",
            "role": "security_officer",
            "subject": "Review security for a task order",
            "template": "emails/invitation.txt",
        },
    ]

    def _update_officer_invitations(self):
        for officer_type in self.OFFICER_INVITATIONS:
            field = officer_type["field"]
            if (
                hasattr(self.form, field)
                and self.form[field].data
                and not getattr(self.task_order, officer_type["role"])
            ):
                prefix = officer_type["prefix"]
                officer_data = {
                    field: getattr(self.task_order, prefix + "_" + field)
                    for field in [
                        "first_name",
                        "last_name",
                        "email",
                        "phone_number",
                        "dod_id",
                    ]
                }
                officer = TaskOrders.add_officer(
                    self.user, self.task_order, officer_type["role"], officer_data
                )
                pf_officer_member = PortfolioRoles.get(self.portfolio.id, officer.id)
                invite_service = InvitationService(
                    self.user,
                    pf_officer_member,
                    officer_data["email"],
                    subject=officer_type["subject"],
                    email_template=officer_type["template"],
                )
                invite_service.invite()

    def update(self):
        self._update_task_order()
        self._update_officer_invitations()
        return self.task_order


@task_orders_bp.route("/task_orders/new/get_started")
def get_started():
    return render_template("task_orders/new/get_started.html")  # pragma: no cover


@task_orders_bp.route("/task_orders/new/<int:screen>")
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>")
@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new/<int:screen>")
def new(screen, task_order_id=None, portfolio_id=None):
    workflow = ShowTaskOrderWorkflow(g.current_user, screen, task_order_id)
    return render_template(
        workflow.template,
        current=screen,
        task_order_id=task_order_id,
        task_order=workflow.task_order,
        portfolio_id=portfolio_id,
        screens=workflow.display_screens,
        form=workflow.form,
    )


@task_orders_bp.route("/task_orders/new/<int:screen>", methods=["POST"])
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>", methods=["POST"])
@task_orders_bp.route(
    "/portfolios/<portfolio_id>/task_orders/new/<int:screen>", methods=["POST"]
)
def update(screen, task_order_id=None, portfolio_id=None):
    workflow = UpdateTaskOrderWorkflow(
        g.current_user, http_request.form, screen, task_order_id, portfolio_id
    )

    if workflow.validate():
        workflow.update()
        return redirect(
            url_for(
                "task_orders.new",
                screen=screen + 1,
                task_order_id=workflow.task_order.id,
            )
        )
    else:
        return render_template(
            workflow.template,
            current=screen,
            task_order_id=task_order_id,
            portfolio_id=portfolio_id,
            screens=workflow.display_screens,
            form=workflow.form,
        )
