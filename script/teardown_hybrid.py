import os
import sys
import requests

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from atat.app import make_config
from atat.domain.csp.cloud.hybrid_cloud_provider import HYBRID_PREFIX
from atat.domain.csp.cloud.utils import get_user_principal_token_for_scope
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD


GRAPH_API = "https://graph.microsoft.com"


def delete_tenant_principal_app(token, app_id):
    auth_header = {
        "Authorization": f"Bearer {token}",
    }

    url = f"{GRAPH_API}/v1.0/applications/{app_id}"

    response = requests.delete(url, headers=auth_header)
    response.raise_for_status()


def list_app_registrations(token):
    auth_header = {
        "Authorization": f"Bearer {token}",
    }

    url = f"{GRAPH_API}/v1.0/applications"
    response = requests.get(url, headers=auth_header)
    response.raise_for_status()

    apps = response.json()["value"]

    return [
        (app["displayName"], app["id"])
        for app in apps
        if app["displayName"].startswith(HYBRID_PREFIX)
    ]


def delete_app_registrations(token):
    apps = list_app_registrations(token)
    if len(apps) > 0:
        print("Deleting Hybrid-managed applications...")
        for app_name, app_id in apps:
            delete_tenant_principal_app(token, app_id)
            print(f"  deleted {app_name}")
    else:
        print("No matching applications found in tenant.")


def list_management_groups(token):
    auth_header = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.get(
        "https://management.azure.com/providers/Microsoft.Management/managementGroups?api-version=2020-02-01",
        headers=auth_header,
    )
    response.raise_for_status()
    mgmt_groups = response.json()["value"]

    return [
        (mgmt_group["properties"]["displayName"], mgmt_group["name"])
        for mgmt_group in mgmt_groups
        if mgmt_group["properties"]["displayName"].startswith(HYBRID_PREFIX)
    ]


def delete_management_group(token, mgmt_group_id):
    auth_header = {
        "Authorization": f"Bearer {token}",
    }
    response = requests.delete(
        f"https://management.azure.com/providers/Microsoft.Management/managementGroups/{mgmt_group_id}?api-version=2020-02-01",
        headers=auth_header,
    )
    response.raise_for_status()


def delete_management_groups(token):
    mgmt_groups = list_management_groups(token)
    if len(mgmt_groups) > 0:
        print("Deleting Hybrid-managed management groups...")
        for display_name, mgmt_group_id in mgmt_groups:
            delete_management_group(token, mgmt_group_id)
            print(f"  deleting {display_name}")
    else:
        print("No matching management groups found in tenant.")


if __name__ == "__main__":
    """
    This script deletes applications created by the HybridCloudProvider
    interface. It expects that the ATAT hybrid configuration settings
    referenced below in this function have been set.
    """
    config = make_config()

    required_config = [
        "AZURE_TENANT_ID",
        "AZURE_TENANT_ADMIN_USERNAME",
        "AZURE_TENANT_ADMIN_PASSWORD",
        "AZURE_POWERSHELL_CLIENT_ID",
    ]
    missing_config = [s for s in required_config if config[s] is None]

    if missing_config:
        raise ValueError(
            f"The following config settings must have values: {', '.join(missing_config)}"
        )

    tenant_id, username, password, ps_client_id = [config[s] for s in required_config]

    # Delete App registations (which also deletes connected service principals)
    graph_token = get_user_principal_token_for_scope(
        username, password, tenant_id, GRAPH_API + "/.default"
    )
    delete_app_registrations(graph_token)

    # Delete management_groups
    resource_token = get_user_principal_token_for_scope(
        username,
        password,
        tenant_id,
        AZURE_PUBLIC_CLOUD.endpoints.resource_manager + "/.default",
    )
    delete_management_groups(resource_token)
