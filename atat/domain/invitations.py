from sqlalchemy.orm.exc import NoResultFound
import pendulum

from atat.database import db
from atat.models import ApplicationInvitation, InvitationStatus, PortfolioInvitation
from atat.domain.portfolio_roles import PortfolioRoles
from atat.domain.application_roles import ApplicationRoles

from .exceptions import NotFoundError


class WrongUserError(Exception):
    def __init__(self, user, invite):
        self.user = user
        self.invite = invite

    @property
    def message(self):
        return "User {} with DOD ID {} does not match expected DOD ID {} for invitation {}".format(
            self.user.id, self.user.dod_id, self.invite.user.dod_id, self.invite.id
        )


class ExpiredError(Exception):
    def __init__(self, invite):
        self.invite = invite

    @property
    def message(self):
        return "Invitation {} has expired.".format(self.invite.id)


class InvitationError(Exception):
    def __init__(self, invite):
        self.invite = invite

    @property
    def message(self):
        return "{} has a status of {}".format(self.invite.id, self.invite.status.value)


class BaseInvitations(object):
    model = None
    role_domain_class = None
    # number of minutes a given invitation is considered valid
    EXPIRATION_LIMIT_MINUTES = 360

    @classmethod
    def _get(cls, token):
        try:
            invite = db.session.query(cls.model).filter_by(token=token).one()
        except NoResultFound:
            raise NotFoundError(cls.model.__tablename__)

        return invite

    @classmethod
    def create(cls, inviter, role, member_data, commit=False):
        # pylint: disable=not-callable
        invite = cls.model(
            role=role,
            inviter=inviter,
            user=role.user,
            status=InvitationStatus.PENDING,
            expiration_time=cls.current_expiration_time(),
            email=member_data.get("email"),
            dod_id=member_data.get("dod_id"),
            first_name=member_data.get("first_name"),
            phone_number=member_data.get("phone_number"),
            last_name=member_data.get("last_name"),
        )
        db.session.add(invite)

        if commit:
            db.session.commit()

        return invite

    @classmethod
    def accept(cls, user, token):
        invite = cls._get(token)

        if invite.dod_id != user.dod_id:
            if invite.is_pending:
                cls._update_status(invite, InvitationStatus.REJECTED_WRONG_USER)
            raise WrongUserError(user, invite)

        elif invite.is_expired:
            cls._update_status(invite, InvitationStatus.REJECTED_EXPIRED)
            raise ExpiredError(invite)

        elif invite.is_accepted or invite.is_revoked or invite.is_rejected:
            raise InvitationError(invite)

        elif invite.is_pending:  # pragma: no branch
            cls._update_status(invite, InvitationStatus.ACCEPTED)
            cls.role_domain_class.enable(invite.role, user)
            return invite

    @classmethod
    def current_expiration_time(cls):
        return pendulum.now(tz="utc").add(minutes=cls.EXPIRATION_LIMIT_MINUTES)

    @classmethod
    def _update_status(cls, invite, new_status):
        invite.status = new_status
        db.session.add(invite)
        db.session.commit()

        return invite

    @classmethod
    def revoke(cls, token):
        invite = cls._get(token)
        invite = cls._update_status(invite, InvitationStatus.REVOKED)
        cls.role_domain_class.disable(invite.role)
        return invite

    @classmethod
    def resend(cls, inviter, token, user_info=None):
        previous_invitation = cls._get(token)
        cls._update_status(previous_invitation, InvitationStatus.REVOKED)

        if not user_info:
            user_info = {
                "email": previous_invitation.email,
                "dod_id": previous_invitation.dod_id,
                "first_name": previous_invitation.first_name,
                "last_name": previous_invitation.last_name,
                "phone_number": previous_invitation.phone_number,
                "phone_ext": previous_invitation.phone_ext,
            }

        return cls.create(inviter, previous_invitation.role, user_info, commit=True)


class PortfolioInvitations(BaseInvitations):
    model = PortfolioInvitation
    role_domain_class = PortfolioRoles


class ApplicationInvitations(BaseInvitations):
    model = ApplicationInvitation
    role_domain_class = ApplicationRoles
