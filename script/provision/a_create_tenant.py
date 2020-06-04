import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from script.provision.provision_base import handle

from atat.domain.csp.cloud.models import TenantCSPPayload


def create_tenant(csp, inputs):
    create_tenant_payload = TenantCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )

    creds = None

    def get_creds(tenant_id, new_creds):
        nonlocal creds
        creds = new_creds

    csp.update_tenant_creds = get_creds
    result = csp.create_tenant(create_tenant_payload)

    # Update inputs with credential information. This will be written to file inside handle().
    # Note: The current implementation of Mock CSP doesn't call update_tenant_creds()
    if creds:
        inputs.get("creds").update({k: v for k, v in creds.dict().items() if v})

    return dict(result)


if __name__ == "__main__":
    handle(create_tenant)
