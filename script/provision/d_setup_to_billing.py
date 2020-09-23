import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    TaskOrderBillingCreationCSPPayload,
    TaskOrderBillingVerificationCSPPayload,
)
from script.provision.provision_base import handle, verify_async


def setup_to_billing(csp, inputs):
    enable_to_billing = TaskOrderBillingCreationCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_task_order_billing_creation(enable_to_billing).dict()

    # If there is a verify URL, then we need to poll for the result.
    if result.get("task_order_billing_verify_url"):
        csp_method = csp.create_task_order_billing_verification
        payload = TaskOrderBillingVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **result,}
        )
        retry_after = result.get("task_order_retry_after")
        result = verify_async(csp_method, payload, retry_after)

    return result


if __name__ == "__main__":
    handle(setup_to_billing)
