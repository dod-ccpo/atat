# Kubernetes Deployment Configuration

This folder contains Kubernetes deployment configuration for Azure. The following assumes that you have `kubectl` installed and configured with permissions to a Kubernetes cluster.

## Applying K8s configuration

Applying the K8s config relies on a combination of kustomize and envsubst. Kustomize comes packaged with kubectl v0.14 and higher. envsubst is part of the gettext package. It can be installed with `brew install gettext` for MacOS users.

The production configuration (azure.atat.code.mil, currently) is reflected in the configuration found in the `deploy/azure` directory. Configuration for a staging environment relies on kustomize to overwrite the production config with values appropriate for that environment. You can find more information about using kustomize [here](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/). Kustomize does not manage templating, and certain values need to be templated. These include:

- CONTAINER_IMAGE: The ATAT container image to use.
- PORT_PREFIX: "8" for production, "9" for staging.
- MAIN_DOMAIN: The host domain for the environment.
- AUTH_DOMAIN: The host domain for the authentication endpoint for the environment.
- KV_MI_ID: the fully qualified id (path) of the managed identity for the key vault (instructions on retrieving this are down in section on [Setting up FlexVol](#configuring-the-identity)). Example: /subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/RESOURCE_GROUP_NAME/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MANAGED_IDENTITY_NAME
- KV_MI_CLIENT_ID: The client id of the managed identity for the key vault. This is a GUID.
- TENANT_ID: The id of the active directory tenant in which the cluster and it's associated users exist. This is a GUID.

We use envsubst to substitute values for these variables. There is a wrapper script (script/k8s_config) that will output the compiled configuration, using a combination of kustomize and envsubst.

To apply config to the main environment, you should first do a diff to determine whether your new config introduces unexpected changes. These examples assume that all the relevant environment variables listed above have been set:

```
./script/k8s_config deploy/azure | kubectl diff -f -
```

Here, `kubectl kustomize` assembles the config and streams it to STDOUT. We specify environment variables for envsubst to use and pass the names of those env vars as a string argument to envsubst. This is important, because envsubst will override NGINX variables in the NGINX config if you don't limit its scope. Finally, we pipe the result from envsubst to `kubectl diff`, which reports a list of differences. Note that some values tracked by K8s internally might have changed, such as [`generation`](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.16/#objectmeta-v1-meta). This is fine and expected.

If you are satisfied with the output from the diff, you can apply the new config the same way:


```
./script/k8s_config deploy/azure | kubectl apply -f -
```

**Note:** Depending on how your `kubectl` config is set up, these commands may need to be adjusted. If you have configuration for multiple clusters, you may need to specify the `kubectl` context for each command with the `--context` flag (something like `kubectl --context=my-cluster [etc.]` or `kubectl --context=azure [etc.]`).

## Secrets and Configuration

### nginx-htpasswd

If the site is running in dev mode, the `/login-dev` endpoint is available. This endpoint is protected by basic HTTP auth. To create a new password file, run:

```
htpasswd -c ./htpasswd atat
```

Enter a new password string when prompted. Then create the secret:

```
kubectl -n atat create secret generic nginx-htpasswd --from-file=./htpasswd
```

## SSL/TLS

(NOTE: We should get cert-manager working for automatic updates of the certificates.)

The NGINX instance in the ATAT pod handles SSL/TLS termination for both the main domain and authentication domain. The certificates are stored as a k8s TLS secret. Currently, certs are obtained from Let's Encrypt by running certbot in manual mode. This section will walk through the process of renewing the certs.

For context, you should be familiar with [ACME HTTP-01 challenge](https://letsencrypt.org/docs/challenge-types/) method for proving ownership of a domain.

To proceed, you will need to install [certbot](https://certbot.eff.org/docs/install.html). If you are on macOs and have `homebrew` installed, `brew install certbot`. These instructions assume a baseline familiarity with NGINX config, Kubernetes, and `kubectl`.

As a broad overview, we will:

- Ask certbot for certificates for the two domains
- Get ACME challenge data from certbot
- Make that data available to the NGINX container in the ATAT pod in our cluster

Once this is done, certbot will be able to confirm that we own the domains and will issue certificates. Then we can make those certs available as TLS secrets in the cluster.

These steps should work for updating an existing site. If you are setting up HTTPS for a new site, make sure DNS is assigned for your two domains.

### Start certbot

First start certbot in manual mode:

```
certbot --manual
```

If certbot tries to write to directories that require root privileges, you can instead run the following command:
```
certbot --config-dir ~/.certbot/config --work-dir ~/.certbot/workdir --logs-dir ~/.certbot/logs certonly --manual
```
You may be prompted to enter an email address, generally we've used the address of our tech lead in the past. If you asked to subscribe to any newsletters, decline.
You may also be prompted to agree to a terms of services, which you should do. 

You will be prompted to enter the domain names you want a cert for. Enter **both** the main and auth domains as a comma separated list. For instance:

```
jedi.atat.code.mil,jedi-auth.atat.code.mil
```

You must agree to have your IP logged to proceed.

### The ACME challenge files

First you will be presented with an ACME challenge for each of the domains you have inputted. The main idea behind the ACME challenge is that cerbort will request that you update your domain(s) so that a file containing a specific string of text is served from a specific endpoint. Certbot will then attempt to load this new file from this new url to check that you have control over the domain.

The ACME challenges are managed as a Kubernetes ConfigMap resource. An example ConfigMap can be found in `deploy/azure/acme-challenges.yml`. It contains a sample ACME challenge (where "foo" is the file name and "bar" is the secret data). Certbot will present you with a file name and path. Add these as a key and a value to the ConfigMap. As an example, certbot may present a message that looks like this:

```
Create a file containing just this data:

ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw.nqBL619amlBbWsSSfB8zqcZowwEI-sFdok57VDkxTmk

And make it available on your web server at this URL:

http://auth-staging.atat.code.mil/.well-known/acme-challenge/ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw
------------------------------------------------------------------------------------------
Press Enter to Continue
```

You would then update the `deploy/azure/acme-challenges.yml` file to look like this:

```
data:
  foo: |
    bar
  ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw: |
    ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw.nqBL619amlBbWsSSfB8zqcZowwEI-sFdok57VDkxTmk
```

If you are updating multiple domains, certbot will present these messages one after another, for each domain. You can wait until you've gotten all the messages to update the yaml file if you wish.

After you have updated the `acme-challenges.yml` file, you need to apply the updated ConfigMap using the kubectl commands discussed in the "Applying K8s Configuration" section above.

In addition to the the environmental variables listed in the [Applying K8s configuration](#applying-k8s-configuration) section above, you'll also need to set the following additional variables before applying the updated ConfiMap:

- VMSS_CLIENT_ID
- KV_NAME

Pay careful attention to ensure that the container image value is to to date. As a reminder, the container images can be listed with:

`kubectl -n master get doployments -o wide`

As always, first check the diff of the changes you're making. Only the changes to the config map file should be listed. The command below is specific to Bash shells.
```
source .env.cloudzero-pwdev-master && ./script/k8s_config deploy/overlays/cloudzero-pwdev-master/ | kubectl diff -f -
```
Then apply your changes with
```
source .env.cloudzero-pwdev-master && ./script/k8s_config deploy/overlays/cloudzero-pwdev-master/ | kubectl apply -f -
```

Once the updated ConfigMap is applied, you can roll the deployment with some version of:

```
kubectl -n master rollout restart deployment atst
```

This will start new pods for the web service, and the new ACME challenge will be available from the NGINX web server. You can verify this by loading the link certbot provides and verifying that you get the ACME challenge content you expect. If the files are loading correctly, proceed forward with certbot. 

You may need to repeat this process for the second domain. If the validation is successful, certbot will write new certificates to your host machine, typically in a directory such as `~/.certbot/config/live/azure.atat.code.mil/`

You may need to combine the newly created `cert.pem` and `privkey.pem` files into one file. Here's how you might do that:

```sh
cd ~/.certbot/config/live/azure.atat.code.mil/
cp cert.pem all.pem
cat privkey.pem >> all.pem
```

### Create the Key Vault certificate object

Once you have obtained the certs, you can create or update the Key Vault certificate object:

```
az keyvault certificate import --vault-name my-vault-name --name my-cert-object-name --file /path/to/my/all.pem
```

Make sure that the vault name and cert name match the ones used in the FlexVol integration, discussed in "Secrets Management" below.

Once the keyvault entry is updated you will need to restart deployment with these new certs:

`kubectl -n master rollout restart deployment atst`

That's the end of the process of renewing certs using certbot and Let's Encrypt. If everything went well then you should be able to load your site and see the new certificate on it.

### Create the Diffie-Hellman parameters

Diffie-Hellman parameters allow per-session encryption of SSL traffic to help improve security. We currently store our parameters in KeyVault, the value can be updated using the following command. Note: Generating the new paramter can take over 10 minutes and there won't be any output while it's running.
```
az keyvault secret set --vault-name <VAULT NAME> --name <NAME OF PARAM> --value "$(openssl genpkey -genparam -algorithm DH -outform pem -pkeyopt dh_paramgen_prime_len:4096 2> /dev/null)"
```
---

# Secrets Management

Secrets, keys, and certificates are managed from Azure Key Vault. These items are mounted into the containers at runtime using the FlexVol implementation described below.

The following are mounted into the NGINX container in the atst pod:

- The TLS certs for the site
- The DH parameter for TLS connections

These are mounted into every instance of the Flask application container (the atst container, the celery worker, etc.):

- The Azure storage key used to access blob storage (AZURE_STORAGE_KEY)
- The password for the SMTP server used to send mail (MAIL_PASSWORD)
- The Postgres database user password (PGPASSWORD)
- The Redis user password (REDIS_PASSWORD)
- The Flask secret key used for session signing and generating CSRF tokens (SECRET_KEY)

Secrets should be added to Key Vault with the following naming pattern: [branch/environment]-[all-caps config setting name]. Note that Key Vault does not support underscores. Substitute hyphens. For example, the config setting for the SMTP server password is MAIL_SERVER. The corresponding secret name in Key Vault is "master-MAIL-SERVER" for the credential used in the primary environment.These secrets are mounted into the containers via FlexVol.

To add or manage secrets, keys, and certificates in Key Vault, see the [documentation](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli).

# Setting Up FlexVol for Secrets

## Preparing Azure Environment

A Key Vault will need to be created. Save its full id (the full path) for use later.

## Preparing Cluster

The 2 following k8s configs will need to be applied to the cluster. They do not need to be namespaced, the latter will create a `kv` namespace for itself.
```
kubectl apply -f deploy/azure/keyvault/deployment-rbac.yaml
kubectl apply -f deploy/azure/keyvault/kv-flex-vol-installer.yaml
```

## Configuring The Identity

1. Creat the identity in a resource group that is able to manage the cluster (`RESOURCE_GROUP_NAME`). You'll also determine a name for the identity (`MANAGED_IDENTITY_NAME`) that you'll use to refer to the identity later:

    `az identity create -g <RESOURCE_GROUP_NAME> -n <MANAGED_IDENTITY_NAME> -o json`

2. From the resulting JSON, we'll need to use: `id`, `clientId` and `principalId` for subsequent commands and configuration.
Example values:
    ```
    id: "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/RESOURCE_GROUP_NAME/providers/Microsoft.ManagedIdentity/userAssignedIdentities/MANAGED_IDENTITY_NAME"
    clientId: 00000000-0000-0000-0000-000000000000
    principalId: 00000000-0000-0000-0000-000000000000
    ```

    > You can recover these values later by running the following command. Verify you are looking at the correct identity by making sure the end of the first line (id) is the same as the name you provided above. If you want the full details of the identity, leave off the last section.
    >
    >`az identity list -g <RESOURCE_GROUP_NAME> | jq '.[] | select(.type == "Microsoft.ManagedIdentity/userAssignedIdentities") | .id, .clientId, principalId'`

3. Assign the new identity two roles: Managed Identity Operator (for itself) and Reader (of the vault). The `VAULT_ID` can be found in the azure portal.

    ```
    az role assignment create --role "Managed Identity Operator" --assignee <principalId> --scope <id>
    az role assignment create --role Reader --assignee <principalId> --scope <VAULT_ID>
    ```

4. Grant the identity get permissions for each of the types of values the vault can store, Keys, Secrets, and Certificates:
    ```
    az keyvault set-policy -n <VAULT_NAME> --spn <clientId> --key-permissions get --secret-permissions get --certificate-permissions get
    ```

5. The file `deploy/azure/aadpodidentity.yml` is templated via Kustomize, so you'll need to include clientId (as `KV_MI_CLIENT_ID`) and id (as `KV_MI_ID`) of the managed identity as part of the call to Kustomize.

## Using the FlexVol

There are 3 steps to using the FlexVol to access secrets from KeyVault

1. For the resource in which you would like to mount a FlexVol, add a metadata label with the selector from `aadpodidentity.yml`
    ```
    metadata:
      labels:
        app: atst
        role: web
        aadpodidbinding: atat-kv-id-binding
    ```

2. Register the FlexVol as a mount and specifiy which secrets you want to mount, along with the file name they should have. The `keyvaultobjectnames`, `keyvaultobjectaliases`, and `keyvaultobjecttypes` correspond to one another, positionally. They are passed as semicolon delimited strings, examples below.

    ```
    - name: volume-of-secrets
      flexVolume:
        driver: "azure/kv"
        options:
          usepodidentity: "true"
          keyvaultname: "<NAME OF KEY VAULT>"
          keyvaultobjectnames: "mysecret;mykey;mycert"
          keyvaultobjectaliases: "mysecret.pem;mykey.txt;mycert.crt"
          keyvaultobjecttypes: "secret;key;cert"
          tenantid: $TENANT_ID
    ```

3. Tell the resource where to mount your new volume, using the same name that you specified for the volume above.
    ```
    - name: nginx-secret
      mountPath: "/usr/secrets/"
      readOnly: true
    ```

4. Once applied, the directory specified in the `mountPath` argument will contain the files you specified in the flexVolume. In our case, you would be able to do this:
    ```
    $ kubectl exec -it CONTAINER_NAME -c atst ls /usr/secrets
    mycert.crt
    mykey.txt
    mysecret.pem
    ```
