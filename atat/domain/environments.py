from typing import List
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm.exc import NoResultFound

from atat.database import db
from atat.domain.environment_roles import EnvironmentRoles
from atat.models import CLIN, Application, Environment, Portfolio, TaskOrder
from atat.utils import commit_or_raise_already_exists_error

from .exceptions import DisabledError, NotFoundError


class Environments(object):
    @classmethod
    def create(cls, user, application, name):
        environment = Environment(application=application, name=name, creator=user)
        db.session.add(environment)
        commit_or_raise_already_exists_error(message="environment")
        return environment

    @classmethod
    def create_many(cls, user, application, names):
        environments = []
        for name in names:
            if name not in [
                existing_envs.name for existing_envs in application.environments
            ]:
                environment = Environments.create(user, application, name)
                environments.append(environment)

        db.session.add_all(environments)
        return environments

    @classmethod
    def update(cls, environment, new_data):
        if "name" in new_data:
            environment.name = new_data["name"]
        if "cloud_id" in new_data:
            environment.cloud_id = new_data["cloud_id"]

        db.session.add(environment)
        commit_or_raise_already_exists_error(message="environment")
        return environment

    @classmethod
    def get(cls, environment_id):
        try:
            env = (
                db.session.query(Environment)
                .filter_by(id=environment_id, deleted=False)
                .one()
            )
        except NoResultFound:
            raise NotFoundError("environment")

        return env

    @classmethod
    def update_env_role(cls, environment, application_role, new_role):
        env_role = EnvironmentRoles.get_for_update(application_role.id, environment.id)

        if env_role and new_role and (env_role.is_disabled or env_role.deleted):
            raise DisabledError("environment_role", env_role.id)

        if env_role and env_role.role != new_role and not env_role.is_disabled:
            env_role.role = new_role
            db.session.add(env_role)
        elif not env_role and new_role:
            env_role = EnvironmentRoles.create(
                application_role=application_role,
                environment=environment,
                role=new_role,
            )
            db.session.add(env_role)

        if env_role and not new_role and not env_role.is_disabled:
            EnvironmentRoles.disable(env_role.id)

        db.session.commit()

    @classmethod
    def revoke_access(cls, environment, target_user):
        EnvironmentRoles.delete(environment.id, target_user.id)

    @classmethod
    def delete(cls, environment, commit=False):
        environment.deleted = True
        db.session.add(environment)

        for role in environment.roles:
            role.deleted = True
            db.session.add(role)

        if commit:
            db.session.commit()

        # TODO: How do we work around environment deletion being a largely manual process in the CSPs

        return environment

    @classmethod
    def base_provision_query(cls, now):
        return (
            db.session.query(Environment.id)
            .join(Application)
            .join(Portfolio)
            .join(TaskOrder)
            .join(CLIN)
            .filter(CLIN.start_date <= now)
            .filter(CLIN.end_date > now)
            .filter(Environment.deleted == False)
            .filter(
                or_(
                    Environment.claimed_until == None,
                    Environment.claimed_until <= func.now(),
                )
            )
        )

    @classmethod
    def get_environments_pending_creation(cls, now) -> List[UUID]:
        """
        Any environment with an active CLIN that doesn't yet have a `cloud_id`.
        """
        results = (
            cls.base_provision_query(now)
            .filter(
                and_(
                    Application.cloud_id != None,
                    Environment.cloud_id.is_(None),
                    or_(
                        Environment.claimed_until.is_(None),
                        Environment.claimed_until <= func.now(),
                    ),
                )
            )
            .all()
        )
        return [id_ for id_, in results]
