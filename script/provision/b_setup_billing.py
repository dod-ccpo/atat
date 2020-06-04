import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    BillingProfileCreationCSPPayload,
    BillingProfileVerificationCSPPayload,
)
from script.provision.provision_base import handle


def poll_billing(csp, inputs, csp_response):
    if csp_response.get("billing_profile_verify_url") is not None:
        time.sleep(10)
        get_billing_profile = BillingProfileVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **csp_response}
        )
        result = csp.create_billing_profile_verification(get_billing_profile)
        if result.get("status") == "ok":
            csp_response = result.get("body").dict()
            return poll_billing(csp, inputs, csp_response)
        else:
            return result.get("body").dict()
    else:
        return csp_response


def setup_billing(csp, inputs):
    create_billing_profile = BillingProfileCreationCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )

    result = csp.create_billing_profile_creation(create_billing_profile)
    return dict(result)


if __name__ == "__main__":
    handle(setup_billing)
