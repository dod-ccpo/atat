import operator
import random
import string
import factory
from uuid import uuid4
import datetime

from atst.forms import data
from atst.models import *

from atst.domain.invitations import PortfolioInvitations
from atst.domain.permission_sets import PermissionSets
from atst.domain.portfolio_roles import PortfolioRoles


def random_choice(choices):
    return random.choice([k for k, v in choices if k])


def random_service_branch():
    return random_choice(data.SERVICE_BRANCHES)


def random_dod_id():
    return "".join(random.choices(string.digits, k=10))


def random_phone_number():
    return "".join(random.choices(string.digits, k=10))


def random_task_order_number():
    return "-".join([str(random.randint(100, 999)) for _ in range(4)])


def random_past_date(year_min=1, year_max=5):
    return _random_date(year_min, year_max, operator.sub)


def random_future_date(year_min=1, year_max=5):
    return _random_date(year_min, year_max, operator.add)


def _random_date(year_min, year_max, operation):
    if year_min == year_max:
        inc = year_min
    else:
        inc = random.randrange(year_min, year_max)

    return datetime.date(
        operation(datetime.date.today().year, inc),
        random.randrange(1, 12),
        random.randrange(1, 28),
    )


def base_portfolio_permission_sets():
    return [
        PermissionSets.get(prms)
        for prms in PortfolioRoles.DEFAULT_PORTFOLIO_PERMISSION_SETS
    ]


def base_application_permission_sets():
    return [PermissionSets.get(PermissionSets.VIEW_APPLICATION)]


def get_all_portfolio_permission_sets():
    return PermissionSets.get_many(PortfolioRoles.PORTFOLIO_PERMISSION_SETS)


class Base(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def dictionary(cls, **attrs):
        return factory.build(dict, FACTORY_CLASS=cls, **attrs)


class UserFactory(Base):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: uuid4())
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    permission_sets = []
    dod_id = factory.LazyFunction(random_dod_id)
    phone_number = factory.LazyFunction(random_phone_number)
    service_branch = factory.LazyFunction(random_service_branch)
    citizenship = "United States"
    designation = "military"
    date_latest_training = factory.LazyFunction(
        lambda: datetime.date.today()
        + datetime.timedelta(days=-(random.randrange(1, 365)))
    )

    @classmethod
    def create_ccpo(cls, **kwargs):
        return cls.create(permission_sets=PermissionSets.get_all(), **kwargs)


class PortfolioFactory(Base):
    class Meta:
        model = Portfolio

    name = factory.Faker("domain_word")
    defense_component = factory.LazyFunction(random_service_branch)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_applications = kwargs.pop("applications", [])
        owner = kwargs.pop("owner", UserFactory.create())
        members = kwargs.pop("members", [])

        portfolio = super()._create(model_class, *args, **kwargs)

        applications = [
            ApplicationFactory.create(portfolio=portfolio, **p)
            for p in with_applications
        ]

        PortfolioRoleFactory.create(
            portfolio=portfolio,
            user=owner,
            status=PortfolioRoleStatus.ACTIVE,
            permission_sets=get_all_portfolio_permission_sets(),
        )

        for member in members:
            user = member.get("user", UserFactory.create())
            role_name = member["role_name"]

            perms_set = None
            if member.get("permissions_sets"):
                perms_set = [
                    PermissionSets.get(perm_set)
                    for perm_set in member.get("permission_sets")
                ]
            else:
                perms_set = []

            PortfolioRoleFactory.create(
                portfolio=portfolio,
                user=user,
                status=PortfolioRoleStatus.ACTIVE,
                permission_sets=perms_set,
            )

        portfolio.applications = applications
        return portfolio


class ApplicationFactory(Base):
    class Meta:
        model = Application

    portfolio = factory.SubFactory(PortfolioFactory)
    name = factory.Faker("domain_word")
    description = "A test application"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_environments = kwargs.pop("environments", [])
        application = super()._create(model_class, *args, **kwargs)

        # need to create application roles for environment users
        app_members_from_envs = set()
        for env in with_environments:
            with_members = env.get("members", [])
            for member_data in with_members:
                member = member_data.get("user", UserFactory.create())
                app_members_from_envs.add(member)
                # set for environments in case we just created the
                # user for the application
                member_data["user"] = member

        for member in app_members_from_envs:
            ApplicationRoleFactory.create(application=application, user=member)

        environments = [
            EnvironmentFactory.create(application=application, **e)
            for e in with_environments
        ]

        application.environments = environments
        return application


class EnvironmentFactory(Base):
    class Meta:
        model = Environment

    name = factory.Faker("domain_word")
    application = factory.SubFactory(ApplicationFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_members = kwargs.pop("members", [])
        environment = super()._create(model_class, *args, **kwargs)

        for member in with_members:
            user = member.get("user", UserFactory.create())
            role_name = member["role_name"]
            EnvironmentRoleFactory.create(
                environment=environment, role=role_name, user=user
            )

        return environment


class PortfolioRoleFactory(Base):
    class Meta:
        model = PortfolioRole

    portfolio = factory.SubFactory(PortfolioFactory)
    user = factory.SubFactory(UserFactory)
    status = PortfolioRoleStatus.PENDING
    permission_sets = factory.LazyFunction(base_portfolio_permission_sets)


class ApplicationRoleFactory(Base):
    class Meta:
        model = ApplicationRole

    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    status = ApplicationRoleStatus.PENDING
    permission_sets = factory.LazyFunction(base_application_permission_sets)


class EnvironmentRoleFactory(Base):
    class Meta:
        model = EnvironmentRole

    environment = factory.SubFactory(EnvironmentFactory)
    role = random.choice([e.value for e in CSPRole])
    user = factory.SubFactory(UserFactory)


class PortfolioInvitationFactory(Base):
    class Meta:
        model = PortfolioInvitation

    email = factory.Faker("email")
    status = InvitationStatus.PENDING
    expiration_time = PortfolioInvitations.current_expiration_time()


class ApplicationInvitationFactory(Base):
    class Meta:
        model = ApplicationInvitation

    email = factory.Faker("email")
    status = InvitationStatus.PENDING
    expiration_time = PortfolioInvitations.current_expiration_time()


class AttachmentFactory(Base):
    class Meta:
        model = Attachment

    filename = factory.Faker("domain_word")
    object_name = factory.LazyFunction(lambda *args: uuid4().hex)


class TaskOrderFactory(Base):
    class Meta:
        model = TaskOrder

    portfolio = factory.SubFactory(PortfolioFactory)

    clin_01 = factory.LazyFunction(lambda *args: random.randrange(100, 100_000))
    clin_03 = factory.LazyFunction(lambda *args: random.randrange(100, 100_000))
    clin_02 = factory.LazyFunction(lambda *args: random.randrange(100, 100_000))
    clin_04 = factory.LazyFunction(lambda *args: random.randrange(100, 100_000))

    app_migration = random_choice(data.APP_MIGRATION)
    native_apps = random.choice(["yes", "no", "not_sure"])
    complexity = [random_choice(data.APPLICATION_COMPLEXITY)]
    dev_team = [random_choice(data.DEV_TEAM)]
    team_experience = random_choice(data.TEAM_EXPERIENCE)

    scope = factory.Faker("sentence")
    start_date = factory.LazyFunction(
        lambda *args: random_future_date(year_min=1, year_max=1)
    )
    end_date = factory.LazyFunction(
        lambda *args: random_future_date(year_min=2, year_max=5)
    )
    performance_length = random.randint(1, 24)
    csp_estimate = factory.SubFactory(AttachmentFactory)

    ko_first_name = factory.Faker("first_name")
    ko_last_name = factory.Faker("last_name")
    ko_email = factory.Faker("email")
    ko_phone_number = factory.LazyFunction(random_phone_number)
    ko_dod_id = factory.LazyFunction(random_dod_id)
    cor_first_name = factory.Faker("first_name")
    cor_last_name = factory.Faker("last_name")
    cor_email = factory.Faker("email")
    cor_phone_number = factory.LazyFunction(random_phone_number)
    cor_dod_id = factory.LazyFunction(random_dod_id)
    so_first_name = factory.Faker("first_name")
    so_last_name = factory.Faker("last_name")
    so_email = factory.Faker("email")
    so_phone_number = factory.LazyFunction(random_phone_number)
    so_dod_id = factory.LazyFunction(random_dod_id)


class DD254Factory(Base):
    class Meta:
        model = DD254

    certifying_official = factory.Faker("name")
    certifying_official_title = factory.Faker("job")
    certifying_official_address = factory.Faker("address")
    certifying_official_phone = factory.LazyFunction(random_phone_number)
    required_distribution = factory.LazyFunction(
        lambda: [random_choice(data.REQUIRED_DISTRIBUTIONS)]
    )


class NotificationRecipientFactory(Base):
    class Meta:
        model = NotificationRecipient

    email = factory.Faker("email")
