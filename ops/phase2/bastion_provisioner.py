import json
import os
import subprocess
import logging
from os import path
from subprocess import CalledProcessError, CompletedProcess
from typing import Optional, Dict, NoReturn

import click
from click.utils import echo
import sys

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
    "--namespace",
    help="Namespacing of your environment - envvar: NAMESPACE",
    envvar="NAMESPACE",
)
@click.option(
    "--ops_tf_application_container",
    default="tf-application",
    help="Name of the container (folder) in the ops_storage_account that holds the terraform state from application - envvar: OPS_TF_APPLICATION_CONTAINER",
    envvar="OPS_TF_APPLICATION_CONTAINER",
)
@click.option(
    "--ops_config_container",
    default="config",
    help="Name of the container (folder) in the ops_storage_account that holds the config that will be needed by the application - envvar: OPS_CONFIG_CONTAINER",
    envvar="OPS_CERTS_CONTAINER",
)
def provision(
    sp_client_id,
    sp_client_secret,
    subscription_id,
    tenant_id,
    ops_resource_group,
    ops_storage_account,
    namespace,
    ops_tf_application_container,
    ops_config_container,
):
    login(sp_client_id, sp_client_secret, subscription_id, tenant_id)

    download_file(
        ops_storage_account,
        ops_config_container,
        "ccpo_users.yml",
        "/tmp/ccpo_users.yml",
    )

    terraform_application(
        backend_resource_group_name=ops_resource_group,
        backend_storage_account_name=ops_storage_account,
        backend_container_name=ops_tf_application_container,
    )

    tf_output_dict = collect_terraform_outputs()

    ansible(
        tf_output_dict=tf_output_dict,
        addl_args={
            "sp_client_id": sp_client_id,
            "sp_client_secret": sp_client_secret,
            "subscription_id": subscription_id,
            "tenant_id": tenant_id,
            "backend_resource_group_name": ops_resource_group,
            "backend_storage_account_name": ops_storage_account,
            "ops_config_container": ops_config_container,
        },
    )

    # deploy
    subprocess.run(
        "helm repo add csi-secrets-store-provider-azure https://raw.githubusercontent.com/Azure/secrets-store-csi-driver-provider-azure/master/charts".split()
    ).check_returncode()
    subprocess.run(
        "helm install csi-secrets-store-provider-azure/csi-secrets-store-provider-azure --generate-name".split()
    )


def login(sp_client_id, sp_client_secret, subscription_id, tenant_id):
    os.environ["ARM_CLIENT_ID"] = sp_client_id
    os.environ["ARM_CLIENT_SECRET"] = sp_client_secret
    os.environ["ARM_SUBSCRIPTION_ID"] = subscription_id
    os.environ["ARM_TENANT_ID"] = tenant_id
    subprocess.run(
        f"az login --service-principal --username {sp_client_id} --password {sp_client_secret} --tenant {tenant_id}".split()
    ).check_returncode()


def collect_terraform_outputs():
    """Collects terraform output into name/value dict to pass as json to ansible"""
    logger.info("collect_terraform_outputs")

    cwd = path.join("../", "../", "terraform", "providers", "application_env")

    result = subprocess.run(
        "terraform output -json".split(), cwd=cwd, capture_output=True
    )
    result.check_returncode()
    output = json.loads(result.stdout.decode("utf-8"))

    return {k: v["value"] for k, v in output.items() if type(v["value"]) is str}


def terraform_application(
    backend_resource_group_name,
    backend_storage_account_name,
    backend_container_name,
    backend_key="terraform.tfstate",
):

    logger.info("terraform_application")

    cwd = path.join("../", "../", "terraform", "providers", "application_env")

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
        import pdb

        pdb.set_trace()
        raise


def diffie_helman(encryption: int = 4096) -> Optional[subprocess.Popen]:
    logger.info("diffie_helman")
    if path.exists("/tmp/dhparams.pem"):
        return

    return subprocess.Popen(
        ["openssl", "dhparam", "-out", "/tmp/dhparams.pem", "4096",],
        stdout=subprocess.DEVNULL,
    )


def download_file(
    storage_account: str, container_name: str, file_name: str, dest_path: str
) -> int:
    if path.exists(dest_path):
        return 0

    result = subprocess.run(
        f"az storage blob download --account-name {storage_account} --container-name {container_name} --name {file_name} -f {dest_path} --no-progress".split(),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        echo(result.stdout)
        echo(result.stderr)

    return result.returncode


def pause_until_complete(open_process: Optional[subprocess.Popen]):
    logger.info("pause_until_complete")
    if open_process is None:
        return

    while True:
        return_code = open_process.poll()
        if return_code is not None:
            click.echo(f"Return Code {return_code}")
            return return_code == 0


def ansible(tf_output_dict, addl_args):
    extra_vars = {**tf_output_dict, **addl_args}
    extra_vars["postgres_root_cert"] = "../deploy/azure/pgsslrootcert.yml"
    extra_vars["src_dir"] = os.path.abspath(os.path.join(os.getcwd(), "../", "../"))
    cwd = path.join("../", "../", "ansible")
    print(extra_vars)
    cmd = [
        "ansible-playbook",
        "provision.yml",
        "-vvv",
        "--extra-vars",
        json.dumps(extra_vars),
    ]
    subprocess.run(cmd, cwd=cwd).check_returncode()


def login(sp_client_id, sp_client_secret, subscription_id, tenant_id):
    os.environ["ARM_CLIENT_ID"] = sp_client_id
    os.environ["ARM_CLIENT_SECRET"] = sp_client_secret
    os.environ["ARM_SUBSCRIPTION_ID"] = subscription_id
    os.environ["ARM_TENANT_ID"] = tenant_id
    subprocess.run(
        f"az login --service-principal --username {sp_client_id} --password {sp_client_secret} --tenant {tenant_id}".split()
    ).check_returncode()


if __name__ == "__main__":
    provision()
