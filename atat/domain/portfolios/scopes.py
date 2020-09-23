from atat.domain.applications import Applications
from atat.domain.authz import Authorization
from atat.models.permissions import Permissions


class ScopedResource(object):
    """
    An abstract class that represents a resource that is restricted
    in some way by the priveleges of the user viewing that resource.
    """

    def __init__(self, user, resource):
        self.user = user
        self.resource = resource

    def __getattr__(self, name):
        return getattr(self.resource, name)

    def __eq__(self, other):
        return self.resource == other


class ScopedPortfolio(ScopedResource):
    """
    An object that obeys the same API as a Portfolio, but with the added
    functionality that it only returns sub-resources (applications and environments)
    that the given user is allowed to see.
    """

    @property
    def applications(self):
        can_view_all_applications = Authorization.has_portfolio_permission(
            self.user, self.resource, Permissions.VIEW_APPLICATION
        )

        if can_view_all_applications:
            return self.resource.applications
        else:
            return Applications.for_user(self.user, self.resource)
