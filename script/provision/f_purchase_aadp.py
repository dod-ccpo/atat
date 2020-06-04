import os
import sys
import time

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from atat.domain.csp.cloud.models import (
    ProductPurchaseCSPPayload,
    ProductPurchaseVerificationCSPPayload,
)
from script.provision.provision_base import handle


def poll_purchase(csp, inputs, csp_response):
    if csp_response.get("product_purchase_verify_url") is not None:
        time.sleep(10)
        purchase_premium = ProductPurchaseVerificationCSPPayload(
            **{**inputs.get("initial_inputs"), **inputs.get("csp_data"), **csp_response}
        )
        result = csp.create_product_purchase_verification(purchase_premium)
        if result.get("status") == "ok":
            csp_response = result.get("body").dict()
            poll_purchase(csp, inputs, csp_response)
        else:
            return result.get("body").dict()
    else:
        return csp_response


def purchase_aadp(csp, inputs):
    purchase_premium = ProductPurchaseCSPPayload(
        **{**inputs.get("initial_inputs"), **inputs.get("csp_data")}
    )

    result = csp.create_product_purchase(purchase_premium)
    return dict(result)


if __name__ == "__main__":
    handle(purchase_aadp)
