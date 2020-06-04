import json
import os
import pprint
import sys
import argparse

from atat.domain.csp.cloud import (
    AzureCloudProvider,
    HybridCloudProvider,
    MockCloudProvider,
)
from atat.domain.csp.cloud.models import KeyVaultCredentials
from atat.app import make_config


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)


def get_provider_and_inputs(input_path, csp):
    with open(input_path, "r") as input_file:
        details = json.loads(input_file.read())
        creds = details.get("creds")
        config = make_config({"default": details.get("config")})

        cloud = get_provider(csp, config)

        def fake_source_creds(tenant_id=None):
            return KeyVaultCredentials(**creds)

        cloud._source_creds = fake_source_creds

        return cloud, details


def get_provider(csp, config):
    azure = AzureCloudProvider(config)
    mock = MockCloudProvider(config, with_failure=False)
    hybrid = HybridCloudProvider(azure, mock, config)

    if csp == "azure":
        return azure
    elif csp == "mock-test":
        return mock
    elif csp == "hybrid":
        return hybrid


def update_and_write(inputs, result, output_path):
    inputs["csp_data"].update(result)
    print(f"Updated inputs {pprint.pformat(inputs, indent=2)}")
    with open(output_path, "w") as output_file:
        print(f"writing to {output_path}")
        output_file.write(json.dumps(inputs, indent=4))


def handle(f):
    parser = argparse.ArgumentParser(
        description="Process some integers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_path", help="Path to input json file",
    )
    parser.add_argument(
        "output_path", help="Path to output json file",
    )
    parser.add_argument(
        "--csp",
        choices=("mock-test", "azure", "hybrid"),
        default="mock-test",
        help="Set cloud service provider",
    )

    args = parser.parse_args()

    provider, inputs = get_provider_and_inputs(args.input_path, args.csp)
    try:
        result = f(provider, inputs)
        if result:
            print("Writing ")
            update_and_write(inputs, result, args.output_path)
        else:
            print("no result")
    except Exception:
        print("Failed]")
        print(f"Inputs: {inputs}")
        print("Exception:")
        import traceback

        traceback.print_exc()
