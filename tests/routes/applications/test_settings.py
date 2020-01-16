import uuid
from flask import url_for, get_flashed_messages
from unittest.mock import Mock
import datetime
from werkzeug.datastructures import ImmutableMultiDict
import pytest

from tests.factories import *

from atst.domain.applications import Applications
from atst.domain.application_roles import ApplicationRoles
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.invitations import ApplicationInvitations
from atst.domain.common import Paginator
from atst.domain.csp.cloud import GeneralCSPException
from atst.domain.permission_sets import PermissionSets
from atst.models.application_role import Status as ApplicationRoleStatus
from atst.models.environment_role import CSPRole, EnvironmentRole
from atst.models.permissions import Permissions
from atst.forms.application import EditEnvironmentForm
from atst.forms.application_member import UpdateMemberForm
from atst.forms.data import ENV_ROLE_NO_ACCESS as NO_ACCESS
from atst.routes.applications.settings import (
    filter_env_roles_form_data,
    filter_env_roles_data,
    get_environments_obj_for_app,
    handle_create_member,
    handle_update_member,
)

from tests.utils import captured_templates


def test_updating_application_environments_success(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    user_session(portfolio.owner)

    form_data = {"name": "new name a"}

    response = client.post(
        url_for("applications.update_environment", environment_id=environment.id),
        data=form_data,
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        application_id=application.id,
        _external=True,
        fragment="application-environments",
        _anchor="application-environments",
    )
    assert environment.name == "new name a"


def test_update_environment_failure(client, user_session):
    portfolio = PortfolioFactory.create()
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(
        application=application, name="original name"
    )

    user_session(portfolio.owner)

    form_data = {"name": ""}

    response = client.post(
        url_for("applications.update_environment", environment_id=environment.id),
        data=form_data,
    )

    assert response.status_code == 400
    assert environment.name == "original name"


def test_enforces_unique_env_name(client, user_session, session):
    application = ApplicationFactory.create()
    user = application.portfolio.owner
    name = "New Environment"
    environment = EnvironmentFactory.create(application=application, name=name)
    form_data = {"name": name}
    user_session(user)

    session.begin_nested()
    response = client.post(
        url_for("applications.new_environment", application_id=application.id),
        data=form_data,
    )
    session.rollback()

    assert response.status_code == 400


def test_application_settings(client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env1", "env2"},
    )
    user_session(portfolio.owner)
    response = client.get(
        url_for("applications.settings", application_id=application.id)
    )
    assert response.status_code == 200
    # the assertion below is a quick check to prevent regressions -- this ensures that
    # the correct URL for creating a member for an application is _somewhere_ in
    # the settings page.
    assert (
        url_for("applications.create_member", application_id=application.id)
        in response.data.decode()
    )


def test_edit_application_environments_obj(app, client, user_session):
    portfolio = PortfolioFactory.create()
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "Snazzy Application",
        "A new application for me and my friends",
        {"env"},
    )
    env = application.environments[0]
    app_role1 = ApplicationRoleFactory.create(application=application)
    env_role1 = EnvironmentRoleFactory.create(
        application_role=app_role1, environment=env, role=CSPRole.ADMIN
    )
    app_role2 = ApplicationRoleFactory.create(application=application, user=None)
    env_role2 = EnvironmentRoleFactory.create(
        application_role=app_role2, environment=env, role=CSPRole.CONTRIBUTOR
    )

    user_session(portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[-1]

        env_obj = context["environments_obj"][0]
        assert env_obj["name"] == env.name
        assert env_obj["id"] == env.id
        assert isinstance(env_obj["edit_form"], EditEnvironmentForm)
        assert {
            "user_name": app_role1.user_name,
            "status": env_role1.status.value,
        } in env_obj["members"]
        assert {
            "user_name": app_role2.user_name,
            "status": env_role2.status.value,
        } in env_obj["members"]
        assert isinstance(context["audit_events"], Paginator)


def test_get_environments_obj_for_app(app, client, user_session):
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}, {"name": "Hoth"}]
    )
    environments_obj = get_environments_obj_for_app(application)

    assert [environment["name"] for environment in environments_obj] == [
        "Endor",
        "Hoth",
        "Naboo",
    ]


def test_get_members_data(app, client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[
            {
                "name": "testing",
                "members": [{"user": user, "role_name": CSPRole.ADMIN}],
            }
        ],
    )
    environment = application.environments[0]
    app_role = ApplicationRoles.get(user_id=user.id, application_id=application.id)
    env_role = EnvironmentRoles.get(
        application_role_id=app_role.id, environment_id=environment.id
    )

    user_session(application.portfolio.owner)

    with captured_templates(app) as templates:
        response = app.test_client().get(
            url_for("applications.settings", application_id=application.id)
        )

        assert response.status_code == 200
        _, context = templates[-1]

        member = context["members"][0]
        assert member["role_id"] == app_role.id
        assert member["user_name"] == user.full_name
        assert member["permission_sets"] == {
            "perms_team_mgmt": False,
            "perms_env_mgmt": False,
            "perms_del_env": False,
        }
        assert member["environment_roles"] == [
            {
                "environment_id": str(environment.id),
                "environment_name": environment.name,
                "role": env_role.role.value,
            }
        ]
        assert member["role_status"]
        assert isinstance(member["form"], UpdateMemberForm)


def test_user_with_permission_can_update_application(client, user_session):
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        applications=[
            {
                "name": "Awesome Application",
                "description": "It's really awesome!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    application = portfolio.applications[0]
    user_session(owner)
    response = client.post(
        url_for("applications.update", application_id=application.id),
        data={
            "name": "Really Cool Application",
            "description": "A very cool application.",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert application.name == "Really Cool Application"
    assert application.description == "A very cool application."


def test_user_without_permission_cannot_update_application(client, user_session):
    dev = UserFactory.create()
    owner = UserFactory.create()
    portfolio = PortfolioFactory.create(
        owner=owner,
        members=[{"user": dev, "role_name": "developer"}],
        applications=[
            {
                "name": "Great Application",
                "description": "Cool stuff happening here!",
                "environments": [{"name": "dev"}, {"name": "prod"}],
            }
        ],
    )
    application = portfolio.applications[0]
    user_session(dev)
    response = client.post(
        url_for("applications.update", application_id=application.id),
        data={"name": "New Name", "description": "A new description."},
        follow_redirects=True,
    )

    assert response.status_code == 404
    assert application.name == "Great Application"
    assert application.description == "Cool stuff happening here!"


def test_update_application_enforces_unique_name(client, user_session, session):
    portfolio = PortfolioFactory.create()
    name = "Test Application"
    application = ApplicationFactory.create(portfolio=portfolio, name=name)
    dupe_application = ApplicationFactory.create(portfolio=portfolio)
    user_session(portfolio.owner)

    session.begin_nested()
    response = client.post(
        url_for("applications.update", application_id=dupe_application.id),
        data={"name": name, "description": dupe_application.description},
    )
    session.rollback()

    assert response.status_code == 400


def test_user_can_only_access_apps_in_their_portfolio(client, user_session):
    portfolio = PortfolioFactory.create()
    other_portfolio = PortfolioFactory.create(
        applications=[
            {
                "name": "Awesome Application",
                "description": "More cool stuff happening here!",
                "environments": [{"name": "dev"}],
            }
        ]
    )
    other_application = other_portfolio.applications[0]
    user_session(portfolio.owner)

    # user can't view application edit form
    response = client.get(
        url_for("applications.settings", application_id=other_application.id)
    )
    assert response.status_code == 404

    # user can't post update application form
    time_updated = other_application.time_updated
    response = client.post(
        url_for("applications.update", application_id=other_application.id),
        data={"name": "New Name", "description": "A new description."},
    )
    assert response.status_code == 404
    assert time_updated == other_application.time_updated


def test_new_environment(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    num_envs = len(application.environments)

    user_session(user)
    response = client.post(
        url_for("applications.new_environment", application_id=application.id),
        data={"name": "dabea"},
    )

    assert response.status_code == 302
    assert len(application.environments) == num_envs + 1


def test_new_environment_with_bad_data(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    num_envs = len(application.environments)

    user_session(user)
    response = client.post(
        url_for("applications.new_environment", application_id=application.id),
        data={"name": None},
    )

    assert response.status_code == 400
    assert len(application.environments) == num_envs


def test_delete_environment(client, user_session):
    user = UserFactory.create()
    portfolio = PortfolioFactory(owner=user)
    application = ApplicationFactory.create(portfolio=portfolio)
    environment = EnvironmentFactory.create(application=application)

    user_session(user)

    response = client.post(
        url_for("applications.delete_environment", environment_id=environment.id)
    )

    # appropriate response and redirect
    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        application_id=application.id,
        _anchor="application-environments",
        _external=True,
        fragment="application-environments",
    )
    # appropriate flash message
    message = get_flashed_messages()[0]
    assert "deleted" in message["message"]
    assert environment.name in message["message"]
    # deletes environment
    assert len(application.environments) == 0


def test_create_member(monkeypatch, client, user_session, session):
    job_mock = Mock()
    monkeypatch.setattr("atst.jobs.send_mail.delay", job_mock)
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    env = application.environments[0]
    env_1 = application.environments[1]

    user_session(application.portfolio.owner)

    response = client.post(
        url_for("applications.create_member", application_id=application.id),
        data={
            "user_data-first_name": user.first_name,
            "user_data-last_name": user.last_name,
            "user_data-dod_id": user.dod_id,
            "user_data-email": user.email,
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "ADMIN",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-role": NO_ACCESS,
            "environment_roles-1-environment_name": env_1.name,
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "perms_del_env": True,
        },
    )

    assert response.status_code == 302
    expected_url = url_for(
        "applications.settings",
        application_id=application.id,
        fragment="application-members",
        _anchor="application-members",
        _external=True,
    )
    assert response.location == expected_url
    assert len(application.roles) == 1
    environment_roles = application.roles[0].environment_roles
    assert len(environment_roles) == 1
    assert environment_roles[0].environment == env

    invitation = (
        session.query(ApplicationInvitation).filter_by(dod_id=user.dod_id).one()
    )
    assert invitation.role.application == application

    assert job_mock.called


def test_remove_member_success(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create()
    application_role = ApplicationRoleFactory.create(application=application, user=user)

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=application_role.id,
        )
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        _anchor="application-members",
        _external=True,
        application_id=application.id,
        fragment="application-members",
    )


def test_remove_new_member_success(client, user_session):
    application = ApplicationFactory.create()
    application_role = ApplicationRoleFactory.create(application=application, user=None)

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=application_role.id,
        )
    )

    assert response.status_code == 302
    assert response.location == url_for(
        "applications.settings",
        _anchor="application-members",
        _external=True,
        application_id=application.id,
        fragment="application-members",
    )


def test_remove_member_failure(client, user_session):
    user = UserFactory.create()
    application = ApplicationFactory.create()

    user_session(application.portfolio.owner)

    response = client.post(
        url_for(
            "applications.remove_member",
            application_id=application.id,
            application_role_id=uuid.uuid4(),
        )
    )

    assert response.status_code == 404


def test_update_member(client, user_session, session):
    role = PermissionSets.get(PermissionSets.EDIT_APPLICATION_TEAM)
    # create an app role with only edit team perms
    app_role = ApplicationRoleFactory.create(permission_sets=[role])
    application = app_role.application
    env = EnvironmentFactory.create(application=application)
    env_1 = EnvironmentFactory.create(application=application)
    env_2 = EnvironmentFactory.create(application=application)
    # add user to two of the environments: env and env_1
    updated_role = EnvironmentRoleFactory.create(
        environment=env, application_role=app_role, role=CSPRole.ADMIN
    )
    suspended_role = EnvironmentRoleFactory.create(
        environment=env_1, application_role=app_role, role=CSPRole.ADMIN
    )

    user_session(application.portfolio.owner)
    # update the user's app permissions to have edit team and env perms
    # update user's role in env, remove user from env_1, and add user to env_2
    response = client.post(
        url_for(
            "applications.update_member",
            application_id=application.id,
            application_role_id=app_role.id,
        ),
        data={
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "CONTRIBUTOR",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-environment_name": env_1.name,
            "environment_roles-1-disabled": "True",
            "environment_roles-2-environment_id": env_2.id,
            "environment_roles-2-role": "BILLING_READ",
            "environment_roles-2-environment_name": env_2.name,
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "perms_del_env": True,
        },
    )

    assert response.status_code == 302
    expected_url = url_for(
        "applications.settings",
        application_id=application.id,
        fragment="application-members",
        _anchor="application-members",
        _external=True,
    )
    assert response.location == expected_url
    # make sure new application role was not created
    assert len(application.roles) == 1
    # check that new app perms were added
    assert bool(app_role.has_permission_set(PermissionSets.EDIT_APPLICATION_TEAM))
    assert bool(
        app_role.has_permission_set(PermissionSets.EDIT_APPLICATION_ENVIRONMENTS)
    )
    assert bool(
        app_role.has_permission_set(PermissionSets.DELETE_APPLICATION_ENVIRONMENTS)
    )

    environment_roles = application.roles[0].environment_roles
    # check that the user has roles in the correct envs
    assert len(environment_roles) == 3
    assert updated_role.role == CSPRole.CONTRIBUTOR
    assert suspended_role.disabled


def test_revoke_invite(client, user_session):
    invite = ApplicationInvitationFactory.create()
    app_role = invite.role
    application = app_role.application

    user_session(application.portfolio.owner)
    response = client.post(
        url_for(
            "applications.revoke_invite",
            application_id=application.id,
            application_role_id=app_role.id,
        )
    )

    assert invite.is_revoked
    assert app_role.status == ApplicationRoleStatus.DISABLED
    assert app_role.deleted


def test_filter_environment_roles():
    application_role = ApplicationRoleFactory.create(user=None)
    application_role2 = ApplicationRoleFactory.create(
        user=None, application=application_role.application
    )
    application_role3 = ApplicationRoleFactory.create(
        user=None, application=application_role.application
    )

    environment = EnvironmentFactory.create(application=application_role.application)

    EnvironmentRoleFactory.create(
        environment=environment, application_role=application_role
    )
    EnvironmentRoleFactory.create(
        environment=environment, application_role=application_role2
    )

    environment_data = filter_env_roles_form_data(application_role, [environment])
    assert environment_data[0]["role"] != "No Access"

    environment_data = filter_env_roles_form_data(application_role3, [environment])
    assert environment_data[0]["role"] == "No Access"

    def test_resend_invite(client, user_session, session):
        user = UserFactory.create()
        # need to set the time created to yesterday, otherwise the original invite and resent
        # invite have the same time_created and then we can't rely on time to order the invites
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        invite = ApplicationInvitationFactory.create(
            user=user, time_created=yesterday, email="original@example.com"
        )
        app_role = invite.role
        application = app_role.application

        user_session(application.portfolio.owner)
        response = client.post(
            url_for(
                "applications.resend_invite",
                application_id=application.id,
                application_role_id=app_role.id,
            ),
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "dod_id": user.dod_id,
                "email": "an_email@example.com",
            },
        )

        session.refresh(app_role)
        assert response.status_code == 302
        assert invite.is_revoked
        assert app_role.status == ApplicationRoleStatus.PENDING
        assert app_role.latest_invitation.email == "an_email@example.com"


def test_filter_env_roles_data():
    env_a = EnvironmentFactory.create(name="a")
    env_b = EnvironmentFactory.create(name="b")
    env_c = EnvironmentFactory.create(name="c")

    env_role_a = EnvironmentRoleFactory.create(environment=env_a)
    env_role_b = EnvironmentRoleFactory.create(environment=env_b)
    env_role_c = EnvironmentRoleFactory.create(environment=env_c)

    env_role_data = filter_env_roles_data([env_role_b, env_role_c, env_role_a])

    # test that the environments are sorted in alphabetical order by name. Since
    # we're just testing if the names are sorted, in this case we don't need to
    # ensure that the environment roles and environments are associated with the
    # same application.
    assert [env["environment_name"] for env in env_role_data] == ["a", "b", "c"]


@pytest.fixture
def set_g(monkeypatch):
    _g = Mock()
    monkeypatch.setattr("atst.app.g", _g)
    monkeypatch.setattr("atst.routes.applications.settings.g", _g)

    def _set_g(attr, val):
        setattr(_g, attr, val)

    yield _set_g


def test_handle_create_member(monkeypatch, set_g, session):
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    (env, env_1) = application.environments

    job_mock = Mock()
    monkeypatch.setattr("atst.jobs.send_mail.delay", job_mock)
    set_g("current_user", application.portfolio.owner)
    set_g("portfolio", application.portfolio)
    set_g("application", application)

    form_data = ImmutableMultiDict(
        {
            "user_data-first_name": user.first_name,
            "user_data-last_name": user.last_name,
            "user_data-dod_id": user.dod_id,
            "user_data-email": user.email,
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "ADMIN",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-role": NO_ACCESS,
            "environment_roles-1-environment_name": env_1.name,
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "perms_del_env": True,
        }
    )
    handle_create_member(application.id, form_data)

    assert len(application.roles) == 1
    environment_roles = application.roles[0].environment_roles
    assert len(environment_roles) == 1
    assert environment_roles[0].environment == env
    invitation = (
        session.query(ApplicationInvitation).filter_by(dod_id=user.dod_id).one()
    )
    assert invitation.role.application == application
    assert job_mock.called


def test_handle_update_member_success(set_g):
    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    (env, env_1) = application.environments
    app_role = ApplicationRoleFactory(application=application)
    set_g("current_user", application.portfolio.owner)
    set_g("portfolio", application.portfolio)
    set_g("application", application)

    form_data = ImmutableMultiDict(
        {
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "ADMIN",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-role": NO_ACCESS,
            "environment_roles-1-environment_name": env_1.name,
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "perms_del_env": True,
        }
    )
    handle_update_member(application.id, app_role.id, form_data)

    assert len(application.roles) == 1
    assert len(app_role.environment_roles) == 1
    assert app_role.environment_roles[0].environment == env


def test_handle_update_member_with_error(set_g, monkeypatch, mock_logger):
    exception = "An error occurred."

    def _raise_csp_exception(*args, **kwargs):
        raise GeneralCSPException(exception)

    monkeypatch.setattr(
        "atst.domain.environments.Environments.update_env_role", _raise_csp_exception
    )

    user = UserFactory.create()
    application = ApplicationFactory.create(
        environments=[{"name": "Naboo"}, {"name": "Endor"}]
    )
    (env, env_1) = application.environments
    app_role = ApplicationRoleFactory(application=application)
    set_g("current_user", application.portfolio.owner)
    set_g("portfolio", application.portfolio)
    set_g("application", application)

    form_data = ImmutableMultiDict(
        {
            "environment_roles-0-environment_id": env.id,
            "environment_roles-0-role": "ADMIN",
            "environment_roles-0-environment_name": env.name,
            "environment_roles-1-environment_id": env_1.id,
            "environment_roles-1-role": NO_ACCESS,
            "environment_roles-1-environment_name": env_1.name,
            "perms_env_mgmt": True,
            "perms_team_mgmt": True,
            "perms_del_env": True,
        }
    )
    handle_update_member(application.id, app_role.id, form_data)

    assert mock_logger.messages[-1] == exception
