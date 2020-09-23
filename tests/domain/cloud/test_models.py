import pytest
from pydantic import ValidationError

from atat.domain.csp.cloud.models import (
    AZURE_MGMNT_PATH,
    BillingOwnerCSPPayload,
    BillingProfileCreationCSPResult,
    BillingProfileVerificationCSPResult,
    KeyVaultCredentials,
    ManagementGroupCSPPayload,
    ManagementGroupCSPResponse,
    ProductPurchaseVerificationCSPResult,
    TenantCSPResult,
    UserCSPPayload,
    UserRoleCSPPayload,
    class_to_stage,
    stage_to_classname,
)
from atat.domain.csp.cloud.utils import OFFICE_365_DOMAIN
from atat.models.mixins.state_machines import AzureStages


def test_stage_to_classname():
    assert (
        stage_to_classname(AzureStages.BILLING_PROFILE_CREATION.name)
        == "BillingProfileCreation"
    )


@pytest.mark.parametrize(
    "klass, stage",
    [
        (TenantCSPResult, "tenant"),
        (BillingProfileCreationCSPResult, "billing_profile"),
        (BillingProfileVerificationCSPResult, "billing_profile"),
    ],
)
def test_class_to_stage(klass, stage):
    assert class_to_stage(klass) == stage


def test_ManagementGroupCSPPayload_management_group_name():
    # supplies management_group_name when absent
    payload = ManagementGroupCSPPayload(
        tenant_id="any-old-id",
        display_name="Council of Naboo",
        parent_id="Galactic_Senate",
    )
    assert payload.management_group_name
    # validates management_group_name
    with pytest.raises(ValidationError):
        payload = ManagementGroupCSPPayload(
            tenant_id="any-old-id",
            management_group_name="council of Naboo 1%^&",
            display_name="Council of Naboo",
            parent_id="Galactic_Senate",
        )
    # shortens management_group_name to fit
    name = "council_of_naboo".ljust(95, "1")

    assert len(name) > 90
    payload = ManagementGroupCSPPayload(
        tenant_id="any-old-id",
        management_group_name=name,
        display_name="Council of Naboo",
        parent_id="Galactic_Senate",
    )
    assert len(payload.management_group_name) == 90


def test_ManagementGroupCSPPayload_display_name():
    # shortens display_name to fit
    name = "Council of Naboo".ljust(95, "1")
    assert len(name) > 90
    payload = ManagementGroupCSPPayload(
        tenant_id="any-old-id", display_name=name, parent_id="Galactic_Senate"
    )
    assert len(payload.display_name) == 90


def test_ManagementGroupCSPPayload_parent_id():
    full_path = f"{AZURE_MGMNT_PATH}Galactic_Senate"
    # adds full path
    payload = ManagementGroupCSPPayload(
        tenant_id="any-old-id",
        display_name="Council of Naboo",
        parent_id="Galactic_Senate",
    )
    assert payload.parent_id == full_path
    # keeps full path
    payload = ManagementGroupCSPPayload(
        tenant_id="any-old-id", display_name="Council of Naboo", parent_id=full_path
    )
    assert payload.parent_id == full_path


def test_ManagementGroupCSPResponse_id():
    full_id = "/path/to/naboo-123"
    response = ManagementGroupCSPResponse(
        **{"id": "/path/to/naboo-123", "other": "stuff", "name": "foo"}
    )
    assert response.id == full_id


def test_KeyVaultCredentials_enforce_admin_creds():
    with pytest.raises(ValidationError):
        KeyVaultCredentials(tenant_id="an id", tenant_admin_username="C3PO")
    assert KeyVaultCredentials(
        tenant_id="an id",
        tenant_admin_username="C3PO",
        tenant_admin_password="beep boop",
    )


def test_KeyVaultCredentials_enforce_sp_creds():
    with pytest.raises(ValidationError):
        KeyVaultCredentials(tenant_id="an id", tenant_sp_client_id="C3PO")
    assert KeyVaultCredentials(
        tenant_id="an id", tenant_sp_client_id="C3PO", tenant_sp_key="beep boop"
    )


def test_KeyVaultCredentials_enforce_root_creds():
    with pytest.raises(ValidationError):
        KeyVaultCredentials(root_tenant_id="an id", root_sp_client_id="C3PO")
    assert KeyVaultCredentials(
        root_tenant_id="an id", root_sp_client_id="C3PO", root_sp_key="beep boop"
    )


class Test_ProductPurchaseVerificationCSPResult:
    def test_azure_payload(self):
        model = ProductPurchaseVerificationCSPResult(
            **{"properties": {"purchaseDate": "2020/01/01"}}
        )
        assert model.premium_purchase_date == "2020/01/01"

    def test_keywords(self):
        model = ProductPurchaseVerificationCSPResult(premium_purchase_date="2020/01/01")
        assert model.premium_purchase_date == "2020/01/01"


def test_KeyVaultCredentials_merge_credentials():
    old_secret = KeyVaultCredentials(
        tenant_id="foo",
        tenant_admin_username="bar",
        tenant_admin_password="baz",  # pragma: allowlist secret
    )
    new_secret = KeyVaultCredentials(
        tenant_id="foo", tenant_sp_client_id="bip", tenant_sp_key="bop"
    )

    expected_update = KeyVaultCredentials(
        tenant_id="foo",
        tenant_admin_username="bar",
        tenant_admin_password="baz",  # pragma: allowlist secret
        tenant_sp_client_id="bip",
        tenant_sp_key="bop",
    )
    assert old_secret.merge_credentials(new_secret) == expected_update


user_payload = {
    "tenant_id": "123",
    "display_name": "Han Solo",
    "tenant_host_name": "rebelalliance",
    "email": "han@moseisley.cantina",
}


def test_UserCSPPayload_mail_nickname():
    payload = UserCSPPayload(**user_payload)
    assert payload.mail_nickname == f"han.solo"


def test_UserCSPPayload_user_principal_name(app):
    payload = UserCSPPayload(**user_payload)
    assert payload.user_principal_name == f"han.solo@rebelalliance.{OFFICE_365_DOMAIN}"


def test_UserCSPPayload_password():
    payload = UserCSPPayload(**user_payload)
    assert payload.password


class TestBillingOwnerCSPPayload:
    user_payload = {
        "tenant_id": "123",
        "domain_name": "rebelalliance",
        "password_recovery_email_address": "han@moseisley.cantina",
    }

    def test_display_name(self):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert payload.display_name == "billing_admin"

    def test_tenant_host_name(self):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert payload.tenant_host_name == self.user_payload["domain_name"]

    def test_mail_nickname(self):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert payload.mail_nickname == "billing.admin"

    def test_password(self):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert payload.password

    def test_user_principal_name(self, app):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert (
            payload.user_principal_name
            == f"billing.admin@rebelalliance.{OFFICE_365_DOMAIN}"
        )

    def test_email(self):
        payload = BillingOwnerCSPPayload(**self.user_payload)
        assert payload.email == self.user_payload["password_recovery_email_address"]


class TestUserRoleCSPPayload:
    def test_management_group_id_without_path(self):
        payload = UserRoleCSPPayload(
            tenant_id="123",
            management_group_id="mid",
            role="owner",
            user_object_id="123",
        )
        assert payload.management_group_id == f"{AZURE_MGMNT_PATH}mid"

    def test_management_group_id_with_path(self):
        full_path = f"{AZURE_MGMNT_PATH}mid"
        payload = UserRoleCSPPayload(
            tenant_id="123",
            management_group_id=full_path,
            role="owner",
            user_object_id="123",
        )
        assert payload.management_group_id == full_path
