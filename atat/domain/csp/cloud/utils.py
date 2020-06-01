import os
import string
import re
import requests
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD

from flask import current_app as app
from atat.domain.csp.cloud.exceptions import AuthenticationException


def generate_user_principal_name(name, domain_name):
    mail_name = generate_mail_nickname(name)
    return f"{mail_name}@{domain_name}.{app.config.get('OFFICE_365_DOMAIN')}"


ESCAPED_PUNCTUATION = re.escape(string.punctuation)


def generate_mail_nickname(name):
    return re.sub(f"[{ESCAPED_PUNCTUATION} ]+", ".", name).lower()


def get_user_principal_token_for_scope(username, password, tenant_id, scope):
    cloud = AZURE_PUBLIC_CLOUD
    url = f"{cloud.endpoints.active_directory}/{tenant_id}/oauth2/v2.0/token"
    payload = {
        # TODO: client_id should be parameterized
        "client_id": os.environ["AZURE_POWERSHELL_CLIENT_ID"],
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": scope,
    }
    token_response = requests.post(url, data=payload, timeout=30)
    token_response.raise_for_status()
    token = token_response.json().get("access_token")
    if token is None:
        message = f"Failed to get user principal token for scope '{scope}' in tenant '{tenant_id}'"
        app.logger.error(message, exc_info=1)
        raise AuthenticationException(message)
    else:
        return token
