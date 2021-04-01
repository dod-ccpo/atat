import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)


from atat.domain.csp.cloud.models import TenantPrincipalAppCSPPayload
from script.provision.provision_base import handle


def report_clin(csp, inputs):
    payload = TenantPrincipalAppCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_tenant_principal_app(payload)
    return dict(result)


if __name__ == "__main__":
    handle(report_clin)
