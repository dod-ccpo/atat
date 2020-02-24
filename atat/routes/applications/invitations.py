from flask import redirect, url_for, g

from .blueprint import applications_bp
from atat.domain.invitations import ApplicationInvitations


@applications_bp.route("/applications/invitations/<token>", methods=["GET"])
def accept_invitation(token):
    invite = ApplicationInvitations.accept(g.current_user, token)

    return redirect(
        url_for(
            "applications.portfolio_applications",
            portfolio_id=invite.application.portfolio_id,
        )
    )
