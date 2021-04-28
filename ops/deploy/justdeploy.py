import json
import logging
import os
import shutil
import subprocess

from subprocess import CalledProcessError, CompletedProcess
from typing import Optional, Dict, NoReturn

import click
import sys

from click.utils import echo
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pprint import pprint


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--sp_client_id",
    help="Client ID (Also called AppId) of the service principle created in phase1 - envvar: SP_CLIENT_ID",
    prompt="Service Principle used to provision infrastructure",
    envvar="SP_CLIENT_ID",
)
@click.option(
    "--sp_client_secret",
    help="Service Principle's password - envvar: SP_CLIENT_SECRET",
    prompt="Service Principle's password",
    envvar="SP_CLIENT_SECRET",
)
@click.option(
    "--subscription_id",
    help="The SubscriptionId (See subscriptions in Azure portal) that will house these resources - envvar: SUBSCRIPTION_ID",
    prompt="Subscription ID",
    envvar="SUBSCRIPTION_ID",
)
@click.option("--tenant_id", help="tenant id - envvar: TENANT_ID", envvar="TENANT_ID")
@click.option(
    "--namespace",
    help="Namespacing of your environment - envvar: NAMESPACE",
    envvar="NAMESPACE",
)
@click.option(
    "--atat_registry",
    help="Short name of the container registry that k8s will have access to - envvar: ATAT_REGISTRY",
    prompt="Short name of the atat container registry eg:cloudzeroregistry",
    envvar="ATAT_REGISTRY",
)
@click.option(
    "--image-tag",
    help="The tag for the update images (atat & nginx) - envvar: IMAGE_TAG",
    envvar="IMAGE_TAG",
)
@click.option(
    "--ops_resource_group",
    help="Resource group created to hold all the resources for operations only - envvar: OPS_RESOURCE_GROUP",
    prompt="Name of operations resource group",
    envvar="OPS_RESOURCE_GROUP",
)
@click.option(
    "--ops_storage_account",
    help="Name of Storage Account that holds the terraform state and inputs for this process - envvar: OPS_STORAGE_ACCOUNT",
    prompt="Name of Ops Storage Account",
    envvar="OPS_STORAGE_ACCOUNT",
)
@click.option(
    "--ops_tf_application_container",
    default="tf-application",
    help="Name of the container (folder) in the ops_storage_account that holds the terraform state from application - envvar: OPS_TF_APPLICATION_CONTAINER",
    envvar="OPS_TF_APPLICATION_CONTAINER",
)
def deploy(
    sp_client_id,
    sp_client_secret,
    subscription_id,
    tenant_id,
    namespace,
    atat_registry,
    image_tag,
    ops_resource_group,
    ops_storage_account,
    ops_tf_application_container,
):
    setup(
        sp_client_id, sp_client_secret, tenant_id, namespace,
    )

    os.environ["ARM_CLIENT_ID"] = sp_client_id
    os.environ["ARM_CLIENT_SECRET"] = sp_client_secret
    os.environ["ARM_SUBSCRIPTION_ID"] = subscription_id
    os.environ["ARM_TENANT_ID"] = tenant_id

    terraform_application(
        backend_resource_group_name=ops_resource_group,
        backend_storage_account_name=ops_storage_account,
        backend_container_name=ops_tf_application_container,
    )

    tf_output_dict = collect_terraform_outputs()

    # Gather the template variables
    template_variables = {
        **tf_output_dict,
        **{
            "sp_client_id": sp_client_id,
            "sp_client_secret": sp_client_secret,
            "subscription_id": subscription_id,
            "tenant_id": tenant_id,
            "atat_image_tag": image_tag,
            "nginx_image_tag": image_tag,
            "application_container_image": f"{atat_registry}.azurecr.io/atat:{image_tag}",
            "nginx_container_image": f"{atat_registry}.azurecr.io/nginx:{image_tag}",
        },
    }

    interpolate_templates(
        template_dir="deployment_templates",
        output_dir=".deployment.out",
        template_variables=template_variables,
    )

    interpolate_templates(
        template_dir="migration_templates",
        output_dir=".migration.out",
        template_variables=template_variables,
    )

    subprocess.run(f"kubectl -n {namespace} delete jobs --all".split())
    subprocess.run(["kubectl", "apply", "-f", f".migration.out/migration.yml"])
    result = subprocess.run(
        f"kubectl -n {namespace} wait --for=condition=complete --timeout=120s job/migration-{image_tag}".split(),
        capture_output=True,
    )
    if b"condition met" not in result.stdout:
        logger.error("Failed to run migrations")
        raise RuntimeError("Failed to run migrations")

    subprocess.run(["kubectl", "apply", "--kustomize=.deployment.out/"])
    subprocess.run(["kubectl", "-n", namespace, "get", "services"])


def interpolate_templates(
    template_dir: str, output_dir: str, template_variables: Dict
) -> NoReturn:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    for path in os.listdir(template_dir):
        template = env.get_template(path)
        with open(f"{output_dir}/{path}", "w") as output_file:
            output_file.write(template.render(**template_variables))


def terraform_application(
    backend_resource_group_name,
    backend_storage_account_name,
    backend_container_name,
    backend_key="terraform.tfstate",
):

    logger.info("terraform_application")

    cwd = os.path.join("../", "../", "terraform", "providers", "application_env")

    default_args = {"cwd": cwd}

    backend_configs = [
        f"-backend-config=resource_group_name={backend_resource_group_name}",
        f"-backend-config=storage_account_name={backend_storage_account_name}",
        f"-backend-config=container_name={backend_container_name}",
        f"-backend-config=key={backend_key}",
    ]
    try:
        init_cmd = ["terraform", "init", *backend_configs, "."]
        print(init_cmd)
        subprocess.run(init_cmd, **default_args).check_returncode()
    except CalledProcessError as err:
        echo("=" * 50)
        echo(f"Failed running {err.cmd}")
        echo("=" * 50)
        echo(err.stdout)
        echo("=" * 50)
        echo(err.stderr)
        raise


def setup(sp_client_id, sp_client_secret, tenant_id, namespace):
    configure_azcli(
        sp_client_id=sp_client_id,
        sp_client_secret=sp_client_secret,
        tenant_id=tenant_id,
        namespace=namespace,
    )


def configure_azcli(sp_client_id, sp_client_secret, tenant_id, namespace):
    cmd = [
        "az",
        "login",
        "--service-principal",
        "--username",
        sp_client_id,
        "--password",
        sp_client_secret,
        "--tenant",
        tenant_id,
    ]
    print(cmd)
    subprocess.run(cmd).check_returncode()
    subprocess.run("az extension add --name aks-preview".split()).check_returncode()
    subprocess.run("az extension update --name aks-preview".split()).check_returncode()
    subprocess.run(
        "az feature register --name AKS-AzurePolicyAutoApprove --namespace Microsoft.ContainerService".split()
    ).check_returncode()
    subprocess.run(
        "az provider register --namespace Microsoft.ContainerService".split()
    ).check_returncode()
    subprocess.run(
        f"az aks get-credentials -g cloudzero-vpc-{namespace} -n cloudzero-private-k8s-{namespace}".split()
    ).check_returncode()


def collect_terraform_outputs():
    """Collects terraform output into name/value dict to pass as json to ansible"""
    logger.info("collect_terraform_outputs")

    cwd = os.path.join("../", "../", "terraform", "providers", "application_env")

    result = subprocess.run(
        "terraform output -json".split(), cwd=cwd, capture_output=True
    )
    result.check_returncode()
    output = json.loads(result.stdout.decode("utf-8"))

    return {k: v["value"] for k, v in output.items() if type(v["value"]) in [str, int]}


if __name__ == "__main__":
    deploy()
