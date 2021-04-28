import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    ProductPurchaseCSPPayload,
    ProductPurchaseVerificationCSPPayload,
)
from script.provision.provision_base import handle, verify_async


def purchase_aadp(csp, inputs):
    purchase_premium = ProductPurchaseCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )
    result = csp.create_product_purchase(purchase_premium).dict()

    # If there is a verify URL, then we need to poll for the result.
    if result.get("product_purchase_verify_url"):
        csp_method = csp.create_product_purchase_verification
        payload = ProductPurchaseVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **result,}
        )
        retry_after = result.get("product_purchase_retry_after")
        result = verify_async(csp_method, payload, retry_after)

    return result


if __name__ == "__main__":
    handle(purchase_aadp)
