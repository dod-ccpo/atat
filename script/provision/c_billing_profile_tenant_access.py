import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import BillingProfileTenantAccessCSPPayload
from script.provision.provision_base import handle


def grant_access(csp, inputs):
    tenant_access = BillingProfileTenantAccessCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_billing_profile_tenant_access(tenant_access)
    return dict(result)


if __name__ == "__main__":
    handle(grant_access)
