import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    BillingProfileCreationCSPPayload,
    BillingProfileVerificationCSPPayload,
)
from script.provision.provision_base import handle, verify_async


def setup_billing(csp, inputs):
    create_billing_profile = BillingProfileCreationCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_billing_profile_creation(create_billing_profile).dict()

    # If there is a verify URL, then we need to poll for the result.
    if result.get("billing_profile_verify_url"):
        csp_method = csp.create_billing_profile_verification
        payload = BillingProfileVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **result,}
        )
        retry_after = result.get("billing_profile_retry_after")
        result = verify_async(csp_method, payload, retry_after)

    return result


if __name__ == "__main__":
    handle(setup_billing)
