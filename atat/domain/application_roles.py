from itertools import groupby
from typing import List
from uuid import UUID

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func, and_, or_

from atat.database import db
from atat.domain.environment_roles import EnvironmentRoles
from atat.models import Application, ApplicationRole, ApplicationRoleStatus, Portfolio
from .permission_sets import PermissionSets
from .exceptions import NotFoundError


class ApplicationRoles(object):
    @classmethod
    def _permission_sets_for_names(cls, set_names):
        set_names = set(set_names).union({PermissionSets.VIEW_APPLICATION})
        return PermissionSets.get_many(set_names)

    @classmethod
    def create(cls, user, application, permission_set_names):
        application_role = ApplicationRole(
            user=user, application_id=application.id, application=application
        )

        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            permission_set_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role

    @classmethod
    def enable(cls, role, user):
        role.status = ApplicationRoleStatus.ACTIVE
        role.user = user

        db.session.add(role)
        db.session.commit()

    @classmethod
    def get(cls, user_id, application_id):
        try:
            app_role = (
                db.session.query(ApplicationRole)
                .filter_by(user_id=user_id, application_id=application_id)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("application_role")

        return app_role

    @classmethod
    def get_by_id(cls, id_):
        try:
            return (
                db.session.query(ApplicationRole)
                .filter(ApplicationRole.id == id_)
                .filter(ApplicationRole.status != ApplicationRoleStatus.DISABLED)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("application_role")

    @classmethod
    def get_many(cls, ids):
        return (
            db.session.query(ApplicationRole)
            .filter(ApplicationRole.id.in_(ids))
            .filter(ApplicationRole.status != ApplicationRoleStatus.DISABLED)
            .all()
        )

    @classmethod
    def update_permission_sets(cls, application_role, new_perm_sets_names):
        application_role.permission_sets = ApplicationRoles._permission_sets_for_names(
            new_perm_sets_names
        )

        db.session.add(application_role)
        db.session.commit()

        return application_role

    @classmethod
    def _update_status(cls, application_role, new_status):
        application_role.status = new_status
        db.session.add(application_role)
        db.session.commit()

        return application_role

    @classmethod
    def disable(cls, application_role):
        cls._update_status(application_role, ApplicationRoleStatus.DISABLED)
        application_role.deleted = True

        for env in application_role.application.environments:
            EnvironmentRoles.delete(
                application_role_id=application_role.id, environment_id=env.id
            )

        db.session.add(application_role)
        db.session.commit()

    @classmethod
    def get_pending_creation(cls) -> List[List[UUID]]:
        """
        Returns a list of lists of ApplicationRole IDs. The IDs
        should be grouped by user and portfolio.
        """
        results = (
            db.session.query(ApplicationRole.id, ApplicationRole.user_id, Portfolio.id)
            .join(Application, Application.id == ApplicationRole.application_id)
            .join(Portfolio, Portfolio.id == Application.portfolio_id)
            .filter(
                and_(
                    Application.cloud_id.isnot(None),
                    ApplicationRole.deleted == False,
                    ApplicationRole.cloud_id.is_(None),
                    ApplicationRole.user_id.isnot(None),
                    ApplicationRole.status == ApplicationRoleStatus.ACTIVE,
                    or_(
                        ApplicationRole.claimed_until.is_(None),
                        ApplicationRole.claimed_until <= func.now(),
                    ),
                )
            )
        ).all()

        groups = []
        keyfunc = lambda pair: (pair[1], pair[2])
        sorted_results = sorted(results, key=keyfunc)
        for _, g in groupby(sorted_results, keyfunc):
            group = [pair[0] for pair in list(g)]
            groups.append(group)

        return groups
