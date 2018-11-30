import re

from flask import render_template, request as http_request, g, redirect, url_for

from . import workspaces_bp
from atst.routes.workspaces.invitations import send_invite_email
from atst.domain.exceptions import AlreadyExistsError
from atst.domain.projects import Projects
from atst.domain.workspaces import Workspaces
from atst.domain.workspace_roles import WorkspaceRoles, MEMBER_STATUS_CHOICES
from atst.domain.environments import Environments
from atst.domain.environment_roles import EnvironmentRoles
from atst.forms.new_member import NewMemberForm
from atst.forms.edit_member import EditMemberForm
from atst.forms.data import (
    ENVIRONMENT_ROLES,
    ENV_ROLE_MODAL_DESCRIPTION,
    WORKSPACE_ROLE_DEFINITIONS,
)
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.invitations import Invitations


@workspaces_bp.route("/workspaces/<workspace_id>/members")
def workspace_members(workspace_id):
    workspace = Workspaces.get_with_members(g.current_user, workspace_id)
    new_member_name = http_request.args.get("newMemberName")
    resent_invitation_to = http_request.args.get("resentInvitationTo")
    new_member = next(
        filter(lambda m: m.user_name == new_member_name, workspace.members), None
    )
    members_list = [
        {
            "name": k.user_name,
            "status": k.display_status,
            "id": k.user_id,
            "role": k.role_displayname,
            "num_env": k.num_environment_roles,
            "edit_link": url_for(
                "workspaces.view_member", workspace_id=workspace.id, member_id=k.user_id
            ),
        }
        for k in workspace.members
    ]

    return render_template(
        "workspaces/members/index.html",
        workspace=workspace,
        role_choices=WORKSPACE_ROLE_DEFINITIONS,
        status_choices=MEMBER_STATUS_CHOICES,
        members=members_list,
        new_member=new_member,
        resent_invitation_to=resent_invitation_to,
    )


@workspaces_bp.route("/workspaces/<workspace_id>/members/new")
def new_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm()
    return render_template(
        "workspaces/members/new.html", workspace=workspace, form=form
    )


@workspaces_bp.route("/workspaces/<workspace_id>/members/new", methods=["POST"])
def create_member(workspace_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    form = NewMemberForm(http_request.form)
    user = g.current_user

    if form.validate():
        try:
            new_member = Workspaces.create_member(user, workspace, form.data)
            invite = Invitations.create(user, new_member, form.data["email"])
            send_invite_email(g.current_user.full_name, invite.token, invite.email)

            return redirect(
                url_for(
                    "workspaces.workspace_members",
                    workspace_id=workspace.id,
                    newMemberName=new_member.user_name,
                )
            )
        except AlreadyExistsError:
            return render_template(
                "error.html", message="There was an error processing your request."
            )
    else:
        return render_template(
            "workspaces/members/new.html", workspace=workspace, form=form
        )


@workspaces_bp.route("/workspaces/<workspace_id>/members/<member_id>/member_edit")
def view_member(workspace_id, member_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this workspace user",
    )
    member = WorkspaceRoles.get(workspace_id, member_id)
    projects = Projects.get_all(g.current_user, member, workspace)
    form = EditMemberForm(workspace_role=member.role_name)
    editable = g.current_user == member.user
    return render_template(
        "workspaces/members/edit.html",
        workspace=workspace,
        member=member,
        projects=projects,
        form=form,
        choices=ENVIRONMENT_ROLES,
        env_role_modal_description=ENV_ROLE_MODAL_DESCRIPTION,
        EnvironmentRoles=EnvironmentRoles,
        editable=editable,
    )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/members/<member_id>/member_edit", methods=["POST"]
)
def update_member(workspace_id, member_id):
    workspace = Workspaces.get(g.current_user, workspace_id)
    Authorization.check_workspace_permission(
        g.current_user,
        workspace,
        Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
        "edit this workspace user",
    )
    member = WorkspaceRoles.get(workspace_id, member_id)

    ids_and_roles = []
    form_dict = http_request.form.to_dict()
    for entry in form_dict:
        if re.match("env_", entry):
            env_id = entry[4:]
            env_role = form_dict[entry] or None
            ids_and_roles.append({"id": env_id, "role": env_role})

    form = EditMemberForm(http_request.form)
    if form.validate():
        new_role_name = None
        if form.data["workspace_role"] != member.role.name:
            member = Workspaces.update_member(
                g.current_user, workspace, member, form.data["workspace_role"]
            )
            new_role_name = member.role_displayname

        Environments.update_environment_roles(
            g.current_user, workspace, member, ids_and_roles
        )

        return redirect(
            url_for(
                "workspaces.workspace_members",
                workspace_id=workspace.id,
                memberName=member.user_name,
                updatedRole=new_role_name,
            )
        )
    else:
        return render_template(
            "workspaces/members/edit.html",
            form=form,
            workspace=workspace,
            member=member,
        )


@workspaces_bp.route(
    "/workspaces/<workspace_id>/members/<member_id>/revoke_access", methods=["POST"]
)
def revoke_access(workspace_id, member_id):
    revoked_role = Workspaces.revoke_access(g.current_user, workspace_id, member_id)
    return redirect(
        url_for(
            "workspaces.workspace_members",
            workspace_id=workspace_id,
            revokedMemberName=revoked_role.user_name,
        )
    )
