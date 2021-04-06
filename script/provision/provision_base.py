import json
import os
import pprint
import sys
import argparse
import time

from atat.domain.csp.cloud.models import KeyVaultCredentials
from atat.app import make_config, make_app, ApplicationEnvironment
from atat.domain.csp import CSP


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

# Turn off debug-level logs by setting to False
config = make_config({"default": {"DEBUG": True}})
app = make_app(config)

def get_provider_and_inputs(input_path, csp):
    app.logger.debug("get_provider_and_inputs()")
    with open(input_path, "r") as input_file:
        app.logger.debug(f"opened input file: {input_path}")
        details = json.loads(input_file.read())
        creds = details.get("creds")
        config = make_config({"default": details.get("config")})
        
        cloud = CSP(csp, config, with_failure=False).cloud

        def fake_source_creds(tenant_id=None):
            return KeyVaultCredentials(**creds)

        cloud._source_creds = fake_source_creds

        return cloud, details


def update_and_write(inputs, result, output_path):
    inputs["csp_data"].update(result)
    app.logger.debug(f"Updated inputs {pprint.pformat(inputs, indent=2)}")
    with open(output_path, "w") as output_file:
        app.logger.info(f"writing to {output_path}")
        output_file.write(json.dumps(inputs, indent=4))


def handle(f):
    with app.app_context():
        env = config["ENV"]
        app.logger.info(f"ENV: {env}")
        app.logger.info(f"handle({f})")
        parser = argparse.ArgumentParser(
            description="ATAT manual provisioning",
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
            choices=("mock-test", "azure", "hybrid", "ea-hybrid"),
            default="mock-test",
            help="Set cloud service provider",
        )

        args = parser.parse_args()
        app.logger.debug(f"got args: {args}")
 
        provider, inputs = get_provider_and_inputs(args.input_path, args.csp)
        app.logger.debug(f"got provider: {provider}")
        app.logger.debug(f"got inputs: {inputs}")
        try:
            app.logger.info(f"preparing to execute parameterized function: {f}")
            result = f(provider, inputs)
            app.logger.info(f"got result: {result} from function: {f}")
            if result:
                app.logger.info(f"writing output file: {args.output_path}")
                update_and_write(inputs, result, args.output_path)
            else:
                app.logger.info(f"no result returned by function: {f}")
        except Exception as e:
            app.logger.error(f"FAILED while executing function: {f}")

def verify_async(csp_method, payload, retry_after):
    while True:
        response = csp_method(payload)
        if response.reset_stage:
            time.sleep(retry_after)
        else:
            return response.dict()
