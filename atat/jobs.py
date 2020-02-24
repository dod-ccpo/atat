import pendulum
from flask import current_app as app
from smtplib import SMTPException
from azure.core.exceptions import AzureError

from atat.database import db
from atat.domain.application_roles import ApplicationRoles
from atat.domain.applications import Applications
from atat.domain.csp.cloud import CloudProviderInterface
from atat.domain.csp.cloud.utils import generate_user_principal_name
from atat.domain.csp.cloud.exceptions import GeneralCSPException
from atat.domain.csp.cloud.models import (
    ApplicationCSPPayload,
    BillingInstructionCSPPayload,
    EnvironmentCSPPayload,
    UserCSPPayload,
    UserRoleCSPPayload,
)
from atat.domain.environments import Environments
from atat.domain.environment_roles import EnvironmentRoles
from atat.domain.portfolios import Portfolios
from atat.models import CSPRole, JobFailure
from atat.models.mixins.state_machines import FSMStates
from atat.domain.task_orders import TaskOrders
from atat.models.utils import claim_for_update, claim_many_for_update
from atat.queue import celery
from atat.utils.localization import translate


class RecordFailure(celery.Task):
    _ENTITIES = [
        "portfolio_id",
        "application_id",
        "environment_id",
        "environment_role_id",
    ]

    def _derive_entity_info(self, kwargs):
        matches = [e for e in self._ENTITIES if e in kwargs.keys()]
        if matches:
            match = matches[0]
            return {"entity": match.replace("_id", ""), "entity_id": kwargs[match]}
        else:
            return None

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        info = self._derive_entity_info(kwargs)
        if info:
            failure = JobFailure(**info, task_id=task_id)
            db.session.add(failure)
            db.session.commit()


@celery.task(ignore_result=True)
def send_mail(recipients, subject, body, attachments=[]):
    app.mailer.send(recipients, subject, body, attachments)


@celery.task(ignore_result=True)
def send_notification_mail(recipients, subject, body):
    app.logger.info(
        "Sending a notification to these recipients: {}\n\nSubject: {}\n\n{}".format(
            recipients, subject, body
        )
    )
    app.mailer.send(recipients, subject, body)


def do_create_application(csp: CloudProviderInterface, application_id=None):
    application = Applications.get(application_id)

    with claim_for_update(application) as application:

        if application.cloud_id:
            return

        csp_details = application.portfolio.csp_data
        parent_id = csp_details.get("root_management_group_id")
        tenant_id = csp_details.get("tenant_id")
        payload = ApplicationCSPPayload(
            tenant_id=tenant_id, display_name=application.name, parent_id=parent_id
        )

        app_result = csp.create_application(payload)
        application.cloud_id = app_result.id
        db.session.add(application)
        db.session.commit()


def do_create_user(csp: CloudProviderInterface, application_role_ids=None):
    if not application_role_ids:
        return

    app_roles = ApplicationRoles.get_many(application_role_ids)

    with claim_many_for_update(app_roles) as app_roles:

        if any([ar.cloud_id for ar in app_roles]):
            return

        csp_details = app_roles[0].application.portfolio.csp_data
        user = app_roles[0].user

        payload = UserCSPPayload(
            tenant_id=csp_details.get("tenant_id"),
            tenant_host_name=csp_details.get("domain_name"),
            display_name=user.full_name,
            email=user.email,
        )
        result = csp.create_user(payload)
        for app_role in app_roles:
            app_role.cloud_id = result.id
            db.session.add(app_role)

        db.session.commit()
        username = payload.user_principal_name
        send_mail(
            recipients=[user.email],
            subject=translate("email.app_role_created.subject"),
            body=translate(
                "email.app_role_created.body",
                {"url": app.config.get("AZURE_LOGIN_URL"), "username": username},
            ),
        )
        app.logger.info(
            f"Application role created notification email sent. User id: {user.id}"
        )


def do_create_environment(csp: CloudProviderInterface, environment_id=None):
    environment = Environments.get(environment_id)

    with claim_for_update(environment) as environment:

        if environment.cloud_id is not None:
            return

        csp_details = environment.portfolio.csp_data
        parent_id = environment.application.cloud_id
        tenant_id = csp_details.get("tenant_id")
        payload = EnvironmentCSPPayload(
            tenant_id=tenant_id, display_name=environment.name, parent_id=parent_id
        )
        env_result = csp.create_environment(payload)
        environment.cloud_id = env_result.id
        db.session.add(environment)
        db.session.commit()


def do_create_environment_role(csp: CloudProviderInterface, environment_role_id=None):
    env_role = EnvironmentRoles.get_by_id(environment_role_id)

    with claim_for_update(env_role) as env_role:

        if env_role.cloud_id is not None:
            return

        env = env_role.environment
        csp_details = env.portfolio.csp_data
        app_role = env_role.application_role

        role = None
        if env_role.role == CSPRole.ADMIN:
            role = UserRoleCSPPayload.Roles.owner
        elif env_role.role == CSPRole.BILLING_READ:
            role = UserRoleCSPPayload.Roles.billing
        elif env_role.role == CSPRole.CONTRIBUTOR:
            role = UserRoleCSPPayload.Roles.contributor

        payload = UserRoleCSPPayload(
            tenant_id=csp_details.get("tenant_id"),
            management_group_id=env.cloud_id,
            user_object_id=app_role.cloud_id,
            role=role,
        )
        result = csp.create_user_role(payload)

        env_role.cloud_id = result.id
        db.session.add(env_role)
        db.session.commit()

        user = env_role.application_role.user
        domain_name = csp_details.get("domain_name")
        username = generate_user_principal_name(user.full_name, domain_name,)
        send_mail(
            recipients=[user.email],
            subject=translate("email.azure_account_update.subject"),
            body=translate(
                "email.azure_account_update.body",
                {"url": app.config.get("AZURE_LOGIN_URL"), "username": username},
            ),
        )
        app.logger.info(
            f"Notification email sent for environment role creation. User id: {user.id}"
        )


def render_email(template_path, context):
    return app.jinja_env.get_template(template_path).render(context)


def do_work(fn, task, csp, **kwargs):
    try:
        fn(csp, **kwargs)
    except GeneralCSPException as e:
        raise task.retry(exc=e)


def send_PPOC_email(portfolio_dict):
    ppoc_email = portfolio_dict.get("password_recovery_email_address")
    user_id = portfolio_dict.get("user_id")
    domain_name = portfolio_dict.get("domain_name")
    username = generate_user_principal_name(user_id, domain_name)
    send_mail(
        recipients=[ppoc_email],
        subject=translate("email.portfolio_ready.subject"),
        body=translate(
            "email.portfolio_ready.body",
            {
                "password_reset_address": app.config.get("AZURE_LOGIN_URL"),
                "username": username,
            },
        ),
    )


def make_initial_csp_data(portfolio):
    return {
        **portfolio.to_dictionary(),
        "billing_account_name": app.config.get("AZURE_BILLING_ACCOUNT_NAME"),
    }


def do_provision_portfolio(csp: CloudProviderInterface, portfolio_id=None):
    portfolio = Portfolios.get_for_update(portfolio_id)
    fsm = Portfolios.get_or_create_state_machine(portfolio)
    fsm.trigger_next_transition(csp_data=make_initial_csp_data(portfolio))
    if fsm.current_state == FSMStates.COMPLETED:
        send_PPOC_email(portfolio.to_dictionary())


@celery.task(bind=True, base=RecordFailure)
def provision_portfolio(self, portfolio_id=None):
    do_work(do_provision_portfolio, self, app.csp.cloud, portfolio_id=portfolio_id)


@celery.task(bind=True, base=RecordFailure)
def create_application(self, application_id=None):
    do_work(do_create_application, self, app.csp.cloud, application_id=application_id)


@celery.task(bind=True, base=RecordFailure)
def create_user(self, application_role_ids=None):
    do_work(
        do_create_user, self, app.csp.cloud, application_role_ids=application_role_ids
    )


@celery.task(bind=True, base=RecordFailure)
def create_environment_role(self, environment_role_id=None):
    do_work(
        do_create_environment_role,
        self,
        app.csp.cloud,
        environment_role_id=environment_role_id,
    )


@celery.task(bind=True, base=RecordFailure)
def create_environment(self, environment_id=None):
    do_work(do_create_environment, self, app.csp.cloud, environment_id=environment_id)


@celery.task(bind=True)
def dispatch_provision_portfolio(self):
    """
    Iterate over portfolios with a corresponding State Machine that have not completed.
    """
    for portfolio_id in Portfolios.get_portfolios_pending_provisioning(pendulum.now()):
        provision_portfolio.delay(portfolio_id=portfolio_id)


@celery.task(bind=True)
def dispatch_create_application(self):
    for application_id in Applications.get_applications_pending_creation():
        create_application.delay(application_id=application_id)


@celery.task(bind=True)
def dispatch_create_user(self):
    for application_role_ids in ApplicationRoles.get_pending_creation():
        create_user.delay(application_role_ids=application_role_ids)


@celery.task(bind=True)
def dispatch_create_environment_role(self):
    for environment_role_id in EnvironmentRoles.get_pending_creation():
        create_environment_role.delay(environment_role_id=environment_role_id)


@celery.task(bind=True)
def dispatch_create_environment(self):
    for environment_id in Environments.get_environments_pending_creation(
        pendulum.now()
    ):
        create_environment.delay(environment_id=environment_id)


@celery.task(bind=True)
def send_task_order_files(self):
    task_orders = TaskOrders.get_for_send_task_order_files()
    recipients = [app.config.get("MICROSOFT_TASK_ORDER_EMAIL_ADDRESS")]

    for task_order in task_orders:
        subject = translate(
            "email.task_order_sent.subject", {"to_number": task_order.number}
        )
        body = translate("email.task_order_sent.body", {"to_number": task_order.number})

        try:
            file = app.csp.files.download_task_order(task_order.pdf.object_name)
            file["maintype"] = "application"
            file["subtype"] = "pdf"
            send_mail(
                recipients=recipients, subject=subject, body=body, attachments=[file]
            )
        except (AzureError, SMTPException) as err:
            app.logger.exception(err)
            continue

        task_order.pdf_last_sent_at = pendulum.now(tz="UTC")
        db.session.add(task_order)

    db.session.commit()


@celery.task(bind=True)
def create_billing_instruction(self):
    clins = TaskOrders.get_clins_for_create_billing_instructions()
    for clin in clins:
        portfolio = clin.task_order.portfolio

        payload = BillingInstructionCSPPayload(
            tenant_id=portfolio.csp_data.get("tenant_id"),
            billing_account_name=portfolio.csp_data.get("billing_account_name"),
            billing_profile_name=portfolio.csp_data.get("billing_profile_name"),
            initial_clin_amount=clin.obligated_amount,
            initial_clin_start_date=str(clin.start_date),
            initial_clin_end_date=str(clin.end_date),
            initial_clin_type=clin.jedi_clin_number,
            initial_task_order_id=str(clin.task_order_id),
        )

        try:
            app.csp.cloud.create_billing_instruction(payload)
        except (AzureError) as err:
            app.logger.exception(err)
            continue

        clin.last_sent_at = pendulum.now(tz="UTC")
        db.session.add(clin)

    db.session.commit()
