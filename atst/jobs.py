import pendulum
from flask import current_app as app

from atst.database import db
from atst.domain.application_roles import ApplicationRoles
from atst.domain.applications import Applications
from atst.domain.csp.cloud import CloudProviderInterface
from atst.domain.csp.cloud.exceptions import GeneralCSPException
from atst.domain.csp.cloud.models import (
    ApplicationCSPPayload,
    EnvironmentCSPPayload,
    UserCSPPayload,
    UserRoleCSPPayload,
)
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.portfolios import Portfolios
from atst.models import CSPRole, JobFailure
from atst.models.utils import claim_for_update, claim_many_for_update
from atst.queue import celery


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
def send_mail(recipients, subject, body):
    app.mailer.send(recipients, subject, body)


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


def do_create_environment(csp: CloudProviderInterface, environment_id=None):
    environment = Environments.get(environment_id)

    with claim_for_update(environment) as environment:

        if environment.cloud_id is not None:
            return

        csp_details = environment.application.portfolio.csp_data
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
        csp_details = env.application.portfolio.csp_data
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
        # TODO: should send notification email to the user, maybe with their portal login name


def render_email(template_path, context):
    return app.jinja_env.get_template(template_path).render(context)


def do_work(fn, task, csp, **kwargs):
    try:
        fn(csp, **kwargs)
    except GeneralCSPException as e:
        raise task.retry(exc=e)


def do_provision_portfolio(csp: CloudProviderInterface, portfolio_id=None):
    portfolio = Portfolios.get_for_update(portfolio_id)
    fsm = Portfolios.get_or_create_state_machine(portfolio)
    fsm.trigger_next_transition()


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
