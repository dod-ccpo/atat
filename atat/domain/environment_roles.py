from typing import List
from uuid import UUID

from flask import current_app as app
from sqlalchemy import and_, func, or_
from sqlalchemy.orm.exc import NoResultFound

from atat.database import db
from atat.domain.exceptions import NotFoundError
from atat.models import (
    Application,
    ApplicationRole,
    ApplicationRoleStatus,
    Environment,
    EnvironmentRole,
    EnvironmentRoleStatus,
)


class EnvironmentRoles(object):
    @classmethod
    def create(cls, application_role, environment, role):
        env_role = EnvironmentRole(
            application_role=application_role, environment=environment, role=role
        )
        return env_role

    @classmethod
    def get(cls, application_role_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .filter(
                EnvironmentRole.application_role_id == application_role_id,
                EnvironmentRole.environment_id == environment_id,
                EnvironmentRole.deleted == False,
                EnvironmentRole.status != EnvironmentRoleStatus.DISABLED,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def get_by_id(cls, id_) -> EnvironmentRole:
        try:
            return (
                db.session.query(EnvironmentRole).filter(EnvironmentRole.id == id_)
            ).one()
        except NoResultFound:
            raise NotFoundError(cls.resource_name)

    @classmethod
    def get_by_user_and_environment(cls, user_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .join(ApplicationRole)
            .filter(
                ApplicationRole.user_id == user_id,
                EnvironmentRole.environment_id == environment_id,
                EnvironmentRole.deleted == False,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def _update_status(cls, environment_role, new_status):
        environment_role.status = new_status
        db.session.add(environment_role)
        db.session.commit()

        return environment_role

    @classmethod
    def delete(cls, application_role_id, environment_id):
        existing_env_role = EnvironmentRoles.get(application_role_id, environment_id)

        if existing_env_role:
            # TODO: Implement suspension
            existing_env_role.deleted = True
            db.session.add(existing_env_role)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def get_for_application_member(cls, application_role_id):
        return (
            db.session.query(EnvironmentRole)
            .filter(EnvironmentRole.application_role_id == application_role_id)
            .filter(EnvironmentRole.deleted != True)
            .all()
        )

    @classmethod
    def get_pending_creation(cls) -> List[UUID]:
        results = (
            db.session.query(EnvironmentRole.id)
            .join(Environment)
            .join(ApplicationRole)
            .filter(
                and_(
                    Environment.deleted == False,
                    EnvironmentRole.deleted == False,
                    ApplicationRole.deleted == False,
                    ApplicationRole.cloud_id != None,
                    ApplicationRole.status != ApplicationRoleStatus.DISABLED,
                    EnvironmentRole.status != EnvironmentRoleStatus.DISABLED,
                    EnvironmentRole.cloud_id.is_(None),
                    or_(
                        EnvironmentRole.claimed_until.is_(None),
                        EnvironmentRole.claimed_until <= func.now(),
                    ),
                )
            )
            .all()
        )
        return [id_ for id_, in results]

    @classmethod
    def activate(cls, role, cloud_id):
        """Assign a cloud id to an environment role and marks it as active"""

        role.status = EnvironmentRoleStatus.ACTIVE
        role.cloud_id = cloud_id

        db.session.add(role)
        db.session.commit()

    @classmethod
    def disable(cls, environment_role_id):
        environment_role = EnvironmentRoles.get_by_id(environment_role_id)

        if environment_role.cloud_id:
            tenant_id = environment_role.environment.portfolio.tenant_id
            app.csp.cloud.disable_user(tenant_id, environment_role.cloud_id)

        environment_role.status = EnvironmentRoleStatus.DISABLED
        db.session.add(environment_role)
        db.session.commit()

        return environment_role

    @classmethod
    def get_for_update(cls, application_role_id, environment_id):
        existing_env_role = (
            db.session.query(EnvironmentRole)
            .filter(
                EnvironmentRole.application_role_id == application_role_id,
                EnvironmentRole.environment_id == environment_id,
            )
            .one_or_none()
        )
        return existing_env_role

    @classmethod
    def for_user(cls, user_id, portfolio_id):
        return (
            db.session.query(EnvironmentRole)
            .join(ApplicationRole)
            .join(Application)
            .filter(Application.portfolio_id == portfolio_id)
            .filter(ApplicationRole.application_id == Application.id)
            .filter(ApplicationRole.user_id == user_id)
            .all()
        )
