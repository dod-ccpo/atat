from flask import render_template, request as http_request, g, redirect, url_for

from .blueprint import portfolios_bp
from atat.domain.portfolios import Portfolios
from atat.domain.portfolio_roles import PortfolioRoles
from atat.models.portfolio_role import Status as PortfolioRoleStatus
from atat.domain.invitations import PortfolioInvitations
from atat.domain.permission_sets import PermissionSets
from atat.domain.audit_log import AuditLog
from atat.domain.common import Paginator
from atat.forms.portfolio import PortfolioForm
import atat.forms.portfolio_member as member_forms
from atat.models.permissions import Permissions
from atat.domain.authz.decorator import user_can_access_decorator as user_can
from atat.utils import first_or_none
from atat.utils.flash import formatted_flash as flash
from atat.domain.exceptions import UnauthorizedError


def filter_perm_sets_data(member):
    perm_sets_data = {
        "perms_app_mgmt": bool(
            member.has_permission_set(
                PermissionSets.EDIT_PORTFOLIO_APPLICATION_MANAGEMENT
            )
        ),
        "perms_funding": bool(
            member.has_permission_set(PermissionSets.EDIT_PORTFOLIO_FUNDING)
        ),
        "perms_reporting": bool(
            member.has_permission_set(PermissionSets.EDIT_PORTFOLIO_REPORTS)
        ),
        "perms_portfolio_mgmt": bool(
            member.has_permission_set(PermissionSets.EDIT_PORTFOLIO_ADMIN)
        ),
    }

    return perm_sets_data


def filter_members_data(members_list):
    members_data = []
    for member in members_list:
        permission_sets = filter_perm_sets_data(member)
        ppoc = (
            PermissionSets.get(PermissionSets.PORTFOLIO_POC) in member.permission_sets
        )
        member_data = {
            "role_id": member.id,
            "user_name": member.user_name,
            "permission_sets": filter_perm_sets_data(member),
            "status": member.display_status,
            "ppoc": ppoc,
            "form": member_forms.PermissionsForm(permission_sets),
        }

        if not ppoc:
            member_data["update_invite_form"] = (
                member_forms.NewForm(user_data=member.latest_invitation)
                if member.latest_invitation and member.latest_invitation.can_resend
                else member_forms.NewForm()
            )
            member_data["invite_token"] = (
                member.latest_invitation.token
                if member.latest_invitation and member.latest_invitation.can_resend
                else None
            )

        members_data.append(member_data)

    return sorted(members_data, key=lambda member: member["user_name"])


def render_admin_page(portfolio, form=None):
    pagination_opts = Paginator.get_pagination_opts(http_request)
    audit_events = AuditLog.get_portfolio_events(portfolio, pagination_opts)
    portfolio_form = PortfolioForm(obj=portfolio)
    member_list = portfolio.members
    assign_ppoc_form = member_forms.AssignPPOCForm()

    for pf_role in portfolio.roles:
        if pf_role.user != portfolio.owner and pf_role.is_active:
            assign_ppoc_form.role_id.choices += [(pf_role.id, pf_role.full_name)]

    current_member = first_or_none(
        lambda m: m.user_id == g.current_user.id, portfolio.members
    )
    current_member_id = current_member.id if current_member else None

    return render_template(
        "portfolios/admin.html",
        form=form,
        portfolio_form=portfolio_form,
        members=filter_members_data(member_list),
        new_manager_form=member_forms.NewForm(),
        assign_ppoc_form=assign_ppoc_form,
        portfolio=portfolio,
        audit_events=audit_events,
        user=g.current_user,
        current_member_id=current_member_id,
        applications_count=len(portfolio.applications),
    )


@portfolios_bp.route("/portfolios/<portfolio_id>/admin")
@user_can(Permissions.VIEW_PORTFOLIO_ADMIN, message="view portfolio admin page")
def admin(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    return render_admin_page(portfolio)


# Updating PPoC is a post-MVP feature
# @portfolios_bp.route("/portfolios/<portfolio_id>/update_ppoc", methods=["POST"])
# @user_can(Permissions.EDIT_PORTFOLIO_POC, message="update portfolio ppoc")
# def update_ppoc(portfolio_id):  # pragma: no cover
#     role_id = http_request.form.get("role_id")
#
#     portfolio = Portfolios.get(g.current_user, portfolio_id)
#     new_ppoc_role = PortfolioRoles.get_by_id(role_id)
#
#     PortfolioRoles.make_ppoc(portfolio_role=new_ppoc_role)
#
#     flash("primary_point_of_contact_changed", ppoc_name=new_ppoc_role.full_name)
#
#     return redirect(
#         url_for(
#             "portfolios.admin",
#             portfolio_id=portfolio.id,
#             fragment="primary-point-of-contact",
#             _anchor="primary-point-of-contact",
#         )
#     )


@portfolios_bp.route("/portfolios/<portfolio_id>/edit", methods=["POST"])
@user_can(Permissions.EDIT_PORTFOLIO_NAME, message="edit portfolio")
def edit(portfolio_id):
    portfolio = Portfolios.get_for_update(portfolio_id)
    form = PortfolioForm(http_request.form)
    if form.validate():
        Portfolios.update(portfolio, form.data)
        return redirect(
            url_for("applications.portfolio_applications", portfolio_id=portfolio.id)
        )
    else:
        # rerender portfolio admin page
        return render_admin_page(portfolio, form)


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<portfolio_role_id>/delete", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="update portfolio members")
def remove_member(portfolio_id, portfolio_role_id):
    portfolio_role = PortfolioRoles.get_by_id(portfolio_role_id)

    if g.current_user.id == portfolio_role.user_id:
        raise UnauthorizedError(
            g.current_user, "you cant remove yourself from the portfolio"
        )

    portfolio = Portfolios.get(user=g.current_user, portfolio_id=portfolio_id)
    if portfolio_role.user_id == portfolio.owner.id:
        raise UnauthorizedError(
            g.current_user, "you can't delete the portfolios PPoC from the portfolio"
        )

    if (
        portfolio_role.latest_invitation
        and portfolio_role.status == PortfolioRoleStatus.PENDING
    ):
        PortfolioInvitations.revoke(portfolio_role.latest_invitation.token)
    else:
        PortfolioRoles.disable(portfolio_role=portfolio_role)

    flash("portfolio_member_removed", member_name=portfolio_role.full_name)

    return redirect(
        url_for(
            "portfolios.admin",
            portfolio_id=portfolio_id,
            _anchor="portfolio-members",
            fragment="portfolio-members",
        )
    )


@portfolios_bp.route(
    "/portfolios/<portfolio_id>/members/<portfolio_role_id>", methods=["POST"]
)
@user_can(Permissions.EDIT_PORTFOLIO_USERS, message="update portfolio members")
def update_member(portfolio_id, portfolio_role_id):
    form_data = http_request.form
    form = member_forms.PermissionsForm(formdata=form_data)
    portfolio_role = PortfolioRoles.get_by_id(portfolio_role_id)
    portfolio = Portfolios.get(user=g.current_user, portfolio_id=portfolio_id)

    if form.validate() and portfolio.owner_role != portfolio_role:
        PortfolioRoles.update(portfolio_role, form.data["permission_sets"])
        flash("update_portfolio_member", member_name=portfolio_role.full_name)

        return redirect(
            url_for(
                "portfolios.admin",
                portfolio_id=portfolio_id,
                _anchor="portfolio-members",
                fragment="portfolio-members",
            )
        )
    else:
        flash("update_portfolio_member_error", member_name=portfolio_role.full_name)
        return (render_admin_page(portfolio), 400)
