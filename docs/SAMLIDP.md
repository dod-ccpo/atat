# SAML IdP Setup and Info

We are going to use SAML to authenticate users. Until we have an official Identity Provider, we will be using a self-hosted one in our Azure region. This document will talk about how to set that up.

The official Azure guide for this process can be found here: https://docs.microsoft.com/en-us/azure/active-directory/manage-apps/application-saml-sso-configure-api

Below we will go through the steps in that flow and describe what needs to be done for our purposes. All of these steps require an authenticated identity (service principal) that has been granted admin consent for: `Application.Read.All`, `Application.ReadWrite.All`, `Application.ReadWrite.OwnedBy`, `Directory.Read.All`, `Directory.ReadWrite.All`. Once you have that, you'll need to authenticate as the identity:

```
curl --location --request POST 'https://login.microsoftonline.com/<TENANT_ID>/oauth2/v2.0/token' \
--form 'grant_type=client_credentials' \
--form 'client_id=CLIENT_ID_OF_APP' \
--form 'client_secret=CLIENT_SECRET_OF_APP' \
--form 'scope=https://graph.microsoft.com/.default'
```

This will return a json blob, you'll need to save the `access_token` for use in future calls.

1. You first need to create the non-gallery application that will be the basis for our new identity provider. This is achieved by creating a new app registration from a template, in our case the template identifer is `8adf8e6e-67b2-4cf2-a259-e3dc5476c621` (Can be found in [this section of the guide](https://docs.microsoft.com/en-us/azure/active-directory/manage-apps/application-saml-sso-configure-api#create-the-gallery-application))
    ```
        curl --location --request POST 'https://graph.microsoft.com/beta/applicationTemplates/8adf8e6e-67b2-4cf2-a259-e3dc5476c621/instantiate' \
        --header 'Authorization: Bearer <access_token>' \
        --header 'Content-Type: application/json' \
        --data-raw '{
        "displayName": "ATAT SAML Auth"
        }'
    ```

    This will give you a response that contains identifiers that will be needed for subsequent steps. Below they'll be referenced by their path in the results json:

        `application.objectId`
        `servicePrincipal.objectId`

2. Next you'll need to configure the service principal to allow SAML sign-on
    ```
    curl --location --request PATCH 'https://graph.microsoft.com/v1.0/servicePrincipals/<servicePrincipal.objectId>' \
    --header 'Authorization: Bearer <access_token>' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "preferredSingleSignOnMode": "saml"
    }
    '
    ```

3. Now that the service principal is SAML enabled, we need to configure some basic SAML properties, namely the endpoints that our new SAML provider should expect to be called from and return to:

    The Identifier URI is the base URI that saml should expect calls to come from. These need to be unique across apps in a given tenant, you can add a path to create a distinction

    The Redirect URI is the URI that SAML will post back to after authentication is complete.

    The Logut URI is the URI that the SAML IdP will redirect the browser back to after IdP signout is complete

    Note: Azure expects these are secure, so for local testing, you'll need to create self-signed certificates and run localhost securely.

    Some examples of Identifier URIs:

    localhost: https://localhost:8000

    staging: https://staging.atat.dev

    staging dev login: https://staging.atat.dev/login-dev (example of adding a path to make it distinct from the other staging identity)

    The Redirect URIs will likely be the same as the Identifier URI with the appropriate path and `acs` query parameter. Using `acs` as a param is idomatic for Assertion Consumer Service URL, which is the SAML concept it maps to. Same with the Logout URI, it should be the same as the Redirect URI, except with an `sls` query parameter. Example below uses a secure localhost

    ```
    curl --location --request PATCH 'https://graph.microsoft.com/v1.0/applications/<application.objectId>' \
    --header 'Authorization: Bearer <access_token>' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "web": {
            "redirectUris": [
                "https://localhost:8000/login?acs"
            ]
        },
        "identifierUris": [
            "https://localhost:8000"
        ],
        "logoutUrl" "https://localhost:8000/login?sls",
    }'
    ```

4. Additionally, we need to register our login URL with the new service principal. This should reflect the route that will initiate login (e.g. https://staging.atat.dev/login). This will ensure that our IdP knows where to direct the user after logging out. Example below continues, as above, using a secure localhost server.

    ```
    curl --location --request PATCH 'https://graph.microsoft.com/v1.0/servicePrincipals/<servicePrincipal.objectId>' \
    --header 'Authorization: Bearer <access_token>' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "loginUrl": "https://localhost:8000/login",

    }'
    ```

5. Now we need to add a certificate to the SAML provider. In the guide, this is prescribed as being done via the API. Unfortunately, due to [API issues](https://github.com/MicrosoftDocs/azure-docs/issues/58484) that were unresovled at the time of this work, this step needs to be done manually. There are 2 options for cert generation, you can either generate a self-signed cert and upload it to the UI, or have azure create a certificate for you and grab the details.

    To generate your own certificate follow the instructions, otherwise skip to the next section.

    The CN field below should match the domain of the deployed instance of ATAT that will consume the saml service.

    ```
    # generate self-signed certificate
    openssl req -x509 -out saml.crt -keyout saml.key -newkey rsa:2048 -nodes -sha256 -subj '/CN=staging.atat.dev'

    # Convert self-signed certificate to PKCS12
    # You'll be prompted for a password
    openssl pkcs12 -export -out saml.pfx -inkey saml.key -in saml.crt
    ```

    To add a certificate to your SAML provider, do the following:

    1. Navigate to [Enterprise Applications](https://portal.azure.com/#blade/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/AllApps)
    2. Find the application you created in the list and click through to its page. It should have the name you provided in the `displayName` you provided in the first step.
    3. If you've configured it correctly, there should be a `Singe sign-on` link in the left panel, click that.
    4. The third panel should be `SAML Signing Certificate`, click on the `Edit` link on the right side of that section.
    5. If you created a cert above do the following, otherwise skip to the next step:
       1. Choose `Import Certificate`, select the `saml.pfx` file you generated above, and enter the same password in the form that you provided when you generated the `saml.pfx` file. Then click `Add`
    6. If you didn't create a cert above, you can simply click `+ New Certificate` and one will be added to the list for you.
    7. You'll the need to enter a notification email address, currently we're just using our azure account name (e.g. first.last@ttenantname.onmicrosoft.com) but we'll want a prescribed notifcation address in the future
    8. Once all that is done, you can click `Save` and the uploaded certificate should be marked as `Active`. You can dismiss the panel (click `X` in the top right) and you should see the certificate details in the `SAML Signing Certificate` panel

6. Add Groups or Users

   TBD: Do we create a group that all authed users should be added to, or add users directly?

   1. Navigate to [Enterprise Applications](https://portal.azure.com/#blade/Microsoft_AAD_IAM/StartboardApplicationsMenuBlade/AllApps)
   2. Find the application you created in the list and click through to it's page. It should have the name you provided in the `displayName` you provided in the first step.
   3. On the left side, click `Users and Groups`
   4. Click `+ Add Users` above, then follow the on screen prompts to search for and select all the users you want to be able to authenticate through this SAML provider

    Alteratively, you may add these users programmatically. To do so, you'll need the following info:
     * The ID of the user(s) you want to add to the application, listed as the "Object ID" on the user detail page in the portal
     * The Role ID of the "User" role on the service principal. You can find that by requesting the service principal info and looking for the app role with the `displayName` of `"User"`
        ```
        curl --location --request GET 'https://graph.microsoft.com/v1.0/servicePrincipals/<servicePrincipal.objectId>' \
        --header 'Authorization: Bearer <access_token>'

        RESPONSE (truncated):
        "appRoles": [
            {
                "allowedMemberTypes": [
                    "User"
                ],
                "description": "User",
                "displayName": "User",
                "id": "servicePrincipal.userAppRoleId",
                "isEnabled": true,
                "origin": "Application",
                "value": null
            }
        ]
        ```

    Once you have those values, you can do the following call to add users (one at a time):

    ```
    curl --location --request POST 'https://graph.microsoft.com/v1.0/servicePrincipals/servicePrincipal.objectId/appRoleAssignments' \
    --header 'Authorization: Bearer <access_token>' \
    --header 'Content-Type: application/json' \
    --data-raw '{
    "principalId": "objectIdOfUser",
    "principalType": "User",
    "appRoleId":"servicePrincipal.userAppRoleId",
    "resourceId":"servicePrincipal.objectId"
    }'
    ```

    At this point, the Identity provider is ready to be consumed!
