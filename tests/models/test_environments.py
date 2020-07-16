import pytest

from atat.models import AuditEvent
from atat.models.environment_role import CSPRole
from atat.domain.applications import Applications
from atat.domain.environment_roles import EnvironmentRoles

from tests.factories import *
from atat.domain.csp.cloud.models import SubscriptionCreationCSPPayload


def test_add_user_to_environment():
    owner = UserFactory.create()
    developer = UserFactory.create()

    portfolio = PortfolioFactory.create(owner=owner)
    application = Applications.create(
        portfolio.owner,
        portfolio,
        "my test application",
        "It's mine.",
        ["dev", "staging", "prod"],
    )
    dev_environment = application.environments[0]

    application_role = ApplicationRoleFactory.create(
        user=developer, application=application
    )
    EnvironmentRoleFactory.create(
        application_role=application_role,
        environment=dev_environment,
        role=CSPRole.ADMIN,
    )
    assert developer in dev_environment.users


@pytest.mark.audit_log
def test_audit_event_for_environment_deletion(session):
    env = EnvironmentFactory.create(application=ApplicationFactory.create())
    env.deleted = True
    session.add(env)
    session.commit()

    update_event = (
        session.query(AuditEvent)
        .filter(AuditEvent.resource_id == env.id, AuditEvent.action == "update")
        .one()
    )
    assert update_event.changed_state.get("deleted")
    before, after = update_event.changed_state["deleted"]
    assert not before
    assert after


def test_environment_roles_do_not_include_deleted():
    member_list = [
        {"role_name": CSPRole.ADMIN},
        {"role_name": CSPRole.ADMIN},
        {"role_name": CSPRole.ADMIN},
    ]
    env = EnvironmentFactory.create(members=member_list)
    role_1 = env.roles[0]
    role_2 = env.roles[1]

    EnvironmentRoles.delete(role_1.application_role_id, env.id)
    EnvironmentRoles.disable(role_2.id)

    assert len(env.roles) == 2


class TestBuildSubscriptionPayload:
    def test_unique_display_name(self, app):
        # Create 2 Applications with the same name that both have an environment named 'Environment'
        app_1 = ApplicationFactory.create(
            name="Application", environments=[{"name": "Environment", "cloud_id": 123}]
        )
        env_1 = app_1.environments[0]
        app_2 = ApplicationFactory.create(
            name="Application", environments=[{"name": "Environment", "cloud_id": 456}]
        )
        env_2 = app_2.environments[0]
        env_1.portfolio.csp_data = {
            "billing_account_name": "xxxx-xxxx-xxx-xxx",
            "billing_profile_name": "xxxxxxxxxxx:xxxxxxxxxxxxx_xxxxxx",
            "tenant_id": "xxxxxxxxxxx-xxxxxxxxxx-xxxxxxx-xxxxx",
            "billing_profile_properties": {
                "invoice_sections": [{"invoice_section_name": "xxxx-xxxx-xxx-xxx"}]
            },
        }
        env_2.portfolio.csp_data = {
            "billing_account_name": "xxxx-xxxx-xxx-xxx",
            "billing_profile_name": "xxxxxxxxxxx:xxxxxxxxxxxxx_xxxxxx",
            "tenant_id": "xxxxxxxxxxx-xxxxxxxxxx-xxxxxxx-xxxxx",
            "billing_profile_properties": {
                "invoice_sections": [{"invoice_section_name": "xxxx-xxxx-xxx-xxx"}]
            },
        }

        # Create subscription payload for each environment
        payload_1 = env_1.build_subscription_payload(
            app.config["AZURE_BILLING_ACCOUNT_NAME"]
        )
        payload_2 = env_2.build_subscription_payload(
            app.config["AZURE_BILLING_ACCOUNT_NAME"]
        )

        assert payload_1.display_name != payload_2.display_name

    def test_populates_payload_correctly(self, app):
        application = ApplicationFactory.create(
            name="Application", environments=[{"name": "Environment", "cloud_id": 123}]
        )
        environment = application.environments[0]
        account_name = app.config["AZURE_BILLING_ACCOUNT_NAME"]
        profile_name = "fake-profile-name"
        tenant_id = "123"
        section_name = "fake-section-name"

        environment.portfolio.csp_data = {
            "billing_profile_name": profile_name,
            "tenant_id": tenant_id,
            "billing_profile_properties": {
                "invoice_sections": [{"invoice_section_name": section_name}]
            },
        }
        payload = environment.build_subscription_payload(
            app.config["AZURE_BILLING_ACCOUNT_NAME"]
        )

        assert type(payload) == SubscriptionCreationCSPPayload
        # Check all key/value pairs except for display_name because of the appended random string
        expected_items = [
            ("tenant_id", tenant_id),
            ("parent_group_id", environment.cloud_id),
            ("billing_account_name", account_name),
            ("billing_profile_name", profile_name),
            ("invoice_section_name", section_name),
        ]
        payload_items = payload.dict().items()
        for item in expected_items:
            assert item in payload_items
