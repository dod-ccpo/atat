from flask import redirect, render_template, request as http_request, url_for

from . import applications_bp
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.applications import Applications
from atst.forms.app_settings import EnvironmentRolesForm
from atst.forms.application import ApplicationForm, EditEnvironmentForm
from atst.domain.authz.decorator import user_can_access_decorator as user_can
from atst.models.environment_role import CSPRole
from atst.domain.exceptions import NotFoundError
from atst.models.permissions import Permissions
from atst.utils.flash import formatted_flash as flash


def get_environments_obj_for_app(application, form=None):
    environments_obj = []
    for env in application.environments:
        edit_form = None

        if form == None or form.data["id"] != env.id:
            edit_form = EditEnvironmentForm(obj=env)
        else:
            edit_form = form

        env_data = {
            "id": env.id,
            "name": env.name,
            "edit_form": edit_form,
            "members_form": EnvironmentRolesForm(data=data_for_env_members_form(env)),
            "members": sort_env_users_by_role(env),
        }
        environments_obj.append(env_data)

    return environments_obj


def sort_env_users_by_role(env):
    users_dict = {"no_access": []}
    for role in CSPRole:
        users_dict[role.value] = []

    for user in env.application.users:
        if user in env.users:
            role = EnvironmentRoles.get(user.id, env.id)
            users_dict[role.displayname].append(
                {"name": user.full_name, "user_id": user.id}
            )
        else:
            users_dict["no_access"].append({"name": user.full_name, "user_id": user.id})

    return users_dict


def data_for_env_members_form(environment):
    data = {"env_id": environment.id, "team_roles": []}
    for user in environment.users:
        env_role = EnvironmentRoles.get(user.id, environment.id)
        data["team_roles"].append(
            {"name": user.full_name, "user_id": user.id, "role": env_role.displayname}
        )

    return data


def check_users_are_in_application(user_ids, application):
    existing_ids = [str(role.user_id) for role in application.roles]
    for user_id in user_ids:
        if not user_id in existing_ids:
            raise NotFoundError("application user", user_id)
    return True


@applications_bp.route("/applications/<application_id>/settings")
@user_can(Permissions.VIEW_APPLICATION, message="view application edit form")
def settings(application_id):
    # refactor like portfolio admin render function
    application = Applications.get(application_id)
    form = ApplicationForm(name=application.name, description=application.description)

    return render_template(
        "portfolios/applications/settings.html",
        application=application,
        form=form,
        environments_obj=get_environments_obj_for_app(application=application),
    )


@applications_bp.route("/environments/<environment_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_ENVIRONMENT, message="edit application environments")
def update_environment(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application

    env_form = EditEnvironmentForm(obj=environment, formdata=http_request.form)

    if env_form.validate():
        Environments.update(environment=environment, name=env_form.name.data)

        flash("application_environments_updated")

        return redirect(
            url_for(
                "applications.settings",
                application_id=application.id,
                fragment="application-environments",
                _anchor="application-environments",
            )
        )
    else:
        return (
            render_template(
                "portfolios/applications/settings.html",
                application=application,
                form=ApplicationForm(
                    name=application.name, description=application.description
                ),
                environments_obj=get_environments_obj_for_app(
                    application=application, form=env_form
                ),
            ),
            400,
        )


@applications_bp.route("/applications/<application_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_APPLICATION, message="update application")
def update(application_id):
    application = Applications.get(application_id)
    form = ApplicationForm(http_request.form)
    if form.validate():
        application_data = form.data
        Applications.update(application, application_data)

        return redirect(
            url_for(
                "applications.portfolio_applications",
                portfolio_id=application.portfolio_id,
            )
        )
    else:
        return render_template(
            "portfolios/applications/settings.html",
            application=application,
            form=form,
            environments_obj=get_environments_obj_for_app(application=application),
        )


@applications_bp.route("/environments/<environment_id>/roles", methods=["POST"])
@user_can(Permissions.ASSIGN_ENVIRONMENT_MEMBER, message="update environment roles")
def update_env_roles(environment_id):
    environment = Environments.get(environment_id)
    application = environment.application
    env_roles_form = EnvironmentRolesForm(http_request.form)

    if env_roles_form.validate():

        try:
            user_ids = [user["user_id"] for user in env_roles_form.data["team_roles"]]
            check_users_are_in_application(user_ids, application)
        except NotFoundError as err:
            app.logger.warning(
                "User {} requested environment role change for unauthorized user {} in application {}.".format(
                    g.current_user.id, err.resource_id, application.id
                ),
                extra={"tags": ["update", "failure"], "security_warning": True},
            )

            raise (err)
        env_data = env_roles_form.data
        Environments.update_env_roles_by_environment(
            environment_id=environment_id, team_roles=env_data["team_roles"]
        )
        return redirect(url_for("applications.settings", application_id=application.id))
    else:
        # TODO: Create a better pattern to handle when a form doesn't validate
        # if a user is submitting the data via the web page then they
        # should never have any form validation errors
        return render_template(
            "portfolios/applications/settings.html",
            application=application,
            form=ApplicationForm(
                name=application.name, description=application.description
            ),
            environments_obj=get_environments_obj_for_app(application=application),
        )


@applications_bp.route("/applications/<application_id>/delete", methods=["POST"])
@user_can(Permissions.DELETE_APPLICATION, message="delete application")
def delete(application_id):
    application = Applications.get(application_id)
    Applications.delete(application)

    flash("application_deleted", application_name=application.name)

    return redirect(
        url_for(
            "applications.portfolio_applications", portfolio_id=application.portfolio_id
        )
    )
