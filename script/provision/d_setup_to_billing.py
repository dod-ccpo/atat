import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    TaskOrderBillingCreationCSPPayload,
    TaskOrderBillingVerificationCSPPayload,
)
from script.provision.provision_base import handle


def poll_billing(csp, inputs, csp_response):
    if csp_response.get("task_order_billing_verify_url") is not None:
        time.sleep(10)
        enable_to_billing = TaskOrderBillingVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **csp_response}
        )
        result = csp.create_task_order_billing_verification(enable_to_billing)
        if result.get("status") == "ok":
            csp_response = result.get("body").dict()
            return poll_billing(csp, inputs, csp_response)
        else:
            return result.get("body").dict()
    else:
        return csp_response


def setup_to_billing(csp, inputs):
    enable_to_billing = TaskOrderBillingCreationCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_task_order_billing_creation(enable_to_billing)
    return dict(result)


if __name__ == "__main__":
    handle(setup_to_billing)
