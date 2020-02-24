from atat.database import db
from atat.domain.common import Query
from atat.models.audit_event import AuditEvent


class AuditEventQuery(Query):
    model = AuditEvent

    @classmethod
    def get_all(cls, pagination_opts):
        query = db.session.query(cls.model).order_by(cls.model.time_created.desc())
        return cls.paginate(query, pagination_opts)

    @classmethod
    def get_portfolio_events(cls, portfolio_id, pagination_opts):
        query = (
            db.session.query(cls.model)
            .filter(cls.model.portfolio_id == portfolio_id)
            .order_by(cls.model.time_created.desc())
        )
        return cls.paginate(query, pagination_opts)

    @classmethod
    def get_application_events(cls, application_id, pagination_opts):
        query = (
            db.session.query(cls.model)
            .filter(cls.model.application_id == application_id)
            .order_by(cls.model.time_created.desc())
        )
        return cls.paginate(query, pagination_opts)


class AuditLog(object):
    @classmethod
    # TODO: see if this is being used anywhere and remove if not
    def log_system_event(cls, resource, action, portfolio=None):
        return cls._log(resource=resource, action=action, portfolio=portfolio)

    @classmethod
    def get_all_events(cls, pagination_opts=None):
        return AuditEventQuery.get_all(pagination_opts)

    @classmethod
    def get_portfolio_events(cls, portfolio, pagination_opts=None):
        return AuditEventQuery.get_portfolio_events(portfolio.id, pagination_opts)

    @classmethod
    def get_application_events(cls, application, pagination_opts=None):
        return AuditEventQuery.get_application_events(application.id, pagination_opts)

    @classmethod
    def get_by_resource(cls, resource_id):
        return (
            db.session.query(AuditEvent)
            .filter(AuditEvent.resource_id == resource_id)
            .order_by(AuditEvent.time_created.desc())
            .all()
        )

    @classmethod
    def _resource_type(cls, resource):
        return type(resource).__name__.lower()

    @classmethod
    # TODO: see if this is being used anywhere and remove if not
    def _log(cls, user=None, portfolio=None, resource=None, action=None):
        resource_id = resource.id if resource else None
        resource_type = cls._resource_type(resource) if resource else None
        portfolio_id = portfolio.id if portfolio else None

        audit_event = AuditEventQuery.create(
            user=user,
            portfolio_id=portfolio_id,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
        )
        return AuditEventQuery.add_and_commit(audit_event)
