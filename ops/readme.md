# Ansible Flow
Our ansible setup is a bit difficult to follow because:
* it starts / stops
* defers functionality to other tools / platforms (terraform & circlieci)
* passes variables through to those other tools / platforms
* updates its own runtime based on the outputs of these tools / platforms
* runs the same code modules at different points, using flags to trigger different branches of execution

So I've tried to document it in detail. This markdown below charts the flow of execution from a file perspective. But misses the nuance of how some modules embed others

## Files:

* [site.yml](../ansible/site.yml)
  * [infra.yml](../ansible/infra.yml)
    * [role: crypto](../ansible/roles/crypto/tasks/main.yml)
      * Create the dh directory if it does not exist
      * Generate Diffie-Hellman parameters with the default size (4096 bits)
    * [role: bootstrap](../ansible/roles/bootstrap/tasks/main.yml)
      * [fetch atat.pem](../ansible/roles/bootstrap/tasks/pull_atat_pem.yml)
      * [fetch bootstrap vars](../ansible/roles/bootstrap/tasks/pull_tfvars.yml)
      * **if** fetch_bootstrap_state # default false
        * [fetch bootstrap state](../ansible/roles/bootstrap/tasks/pull_remote_state.yml)
      * [get vars](../ansible/roles/bootstrap/tasks/get_variables.yml)
      * **if** deploy_bootstrap_env # default true
        * [bootstrap env](../ansible/roles/bootstrap/tasks/setup.yml)
      * **if** show_bs_env # default true
        * [show outputs from run](../ansible/roles/bootstrap/tasks/show_outputs.yml)
      * **if** deploy_bootstrap_env # default true
        * [push local state to remote](../ansible/roles/bootstrap/tasks/push_state_remote.yml)
    * [role: circleci](../ansible/roles/circle_ci/tasks/main.yml)
      * **PARAMS**
        * build_and_push_ops_image - True
      * [get the circle ci api token](../ansible/roles/circle_ci/tasks/source_api_token.yml)
      * get tf outputs
        * **PARAMS**
          * deploy_app_env: false
        * **WTF** - include_role - terraform - what does this do? - Does this now load terraform's role, and just pass the invluded variable?! Guess that means the defaults here also apply and could override terraform? Shoot me.
      * **if** build_and_push_ops_image
        * [run circle ci ops build](../ansible/roles/circle_ci/tasks/run_ops_build.yml)
          * Kick off a build for image
            * ** ============= RUNS ON CIRCLECI ============= **
          * Fetch latest `ops` image from
            * Polls, waiting on circleci to complete
      * Note, also has build_and_push_app_image, but this is disabled
    * [role: terraform](../ansible/roles/terraform/tasks/main.yml)
      * [get backend config](../ansible/roles/terraform/tasks/get_backend.yml)
        * **TODO: How Does This Work**
          * with_items: "{{ tf_bootstrap_backend_outputs }}"
          * when:
            * item != 'environment'
            * item != 'ops_container_registry_name' -->
        * build backend
          * SETS the b_end fact, such that it will presumably do the real terraform call later
      * [get backend config (dupe name)](../ansible/roles/terraform/tasks/source_vars_from_storage_account.yml)
        * Download tfvars file
          * **TODO** Security check - is this saved to an encrypted drive?
            * /src/terraform/providers/application_env/app.tfvars.json
      * [get variables](../ansible/roles/terraform/tasks/get_variables.yml)
        * **TODO:** This is all just variable setting - don't really follow the commands or intent yet
        * set tf vars file path
        * pull in tfvars values
        * make k/v
      * **if** deploy_app_env
        * [deploy application env](../ansible/roles/terraform/tasks/setup.yml)
          * set tf_dir # Set fact
          * **if** target_modules is defined **AND** b_end is defined
            * tf apply (modules)
              * **Note:** modules means only install the selected modules. It does LESS than no modules, not more
          * **if** target_modules is **NOT** defined **AND** b_end is defined
            * tf apply (no modules)
      * **if** show_app_env_outputs
        * [show outputs](../ansible/roles/terraform/tasks/show_outputs.yml)
    * [role: circle_ci](../ansible/roles/circle_ci/tasks/main.yml)
      * **PARAMS**
        * build_and_push_app_images = True
      * **if** build_and_push_app_images
        * [run circle ci app build](../ansible/roles/circle_ci/tasks/run_app_build.yml)
          * * Kick off a build for image
            * ** ============= RUNS ON CIRCLECI ============= **
      * See above for the other circle ci tasks
    * **if** teardown_bootstrap_env
      * [role: destroy_bootstrap](../ansible/roles/destroy_bootstrap/tasks/main.yml)
        * [get vars](../ansible/roles/destroy_bootstrap/tasks/get_variables.yml)
          * set those same weird variables there is a todo for above
        * [get bootstrap env outputs before destroy](../ansible/roles/destroy_bootstrap/tasks/show_outputs.yml)
        * [destroy bootstrap env](../ansible/roles/destroy_bootstrap/tasks/teardown.yml)
          * tf destroy bootstrap env (no modules)
    * role: azure_keyvault
      * [source the secrets](../ansible/roles/azure_keyvault/tasks/source_secrets.yml)
        * pickup application_env variables # set_fact
        * get app _output # terraform.get_backend.yml
        * include terraform/show_outputs.yml
        * set var values fact # set value
      * [bootstrap keyvault with terraform vars](../ansible/roles/azure_keyvault/tasks/bootstrap_terraform_secrets.yml)
        * store deployment config and outputs values in __vault_name__
      * [store secrets as plain key=value](../ansible/roles/azure_keyvault/tasks/secret.yml)
        * Create secret
      * [secrets to json file](../ansible/roles/azure_keyvault/tasks/secrets_to_json_file.yml)
        * set vault deploy tag # (set_fact)
        * [get_secrets](../ansible/roles/azure_keyvault/tasks/get_secrets.yml)
          * get secrets
          * Include get_secrets
      * [wipe secrets](../ansible/roles/azure_keyvault/tasks/wipe_secrets.yml)
      * [get secrets](../ansible/roles/azure_keyvault/tasks/get_secrets.yml)
  * [databases.yml](../ansible/databases.yml)
    * [role: db](../ansible/roles/db/tasks/main.yml)
      * [source ccpo users file](../ansible/roles/db/tasks/source_ccpo_user_file.yml)
        * Download CCPO Users file from storage account
      * [provision postgres](../ansible/roles/db/tasks/postgres.yml)
        * grab the root cert from yaml
          * seems to just print the cert
        * set cert fact
        * write cert to temp file
        * Create (or update) PostgreSQL Database (azure resource - not in terraform?)
        * Adds uuid-ossp extension to the database
        * Create database user
        * Create database user
        * Initialize database
        * Add CCPO users
  * [k8s.yml](../ansible/k8s.yml)
    * **if** private_cluster_deploy
      * [role: bootstrap](../ansible/roles/bootstrap/tasks/main.yml)
        * **PARAMS**
          * show_bs_env = true
          * bootstrap_init_tf = true
          * deploy_bootstrap_env = false
          * fetch_bootstrap_state = true
        * fetch atat.pem
        * fetch bootstrap vars
        * fetch bootstrap state
        * get vars
        * show outputs from run
      * [role: terraform](../ansible/roles/terraform/tasks/main.yml)
        * **PARAMS**
          * show_app_env_outputs: true
          * deploy_app_env: false
          * init_tf: true
        * get backend config
        * get backend config
        * get variables
        * show outputs
    * role: [role: k8s](../ansible/roles/k8s/tasks/main.yml)
      * [create k8s overlays](../ansible/roles/k8s/tasks/generate_overlays.yml)
        * Create template output directory
        * Interpolate the templates
      * [push overlays to storage bucket](../ansible/roles/k8s/tasks/push_overlays.yml)
        * Compress overlays
        * push overlays to a storage account
      * **if** private_cluster_deploy
        * [configure the private cluster](../ansible/roles/k8s/configure_private_cluster.yml)
          * Download k8s overlays
          * Extract private cluster configs
          * Connect to the {{ namespace }} kubernetes cluster
          * Create {{ namespace }} namespace
          * "Attach the ACR to the K8s cluster"
          * Assign Network Contributor role to the AKS Service Principal for the Virtual Network
          * Get vmss
          * Assign the Vault Reader identity to the AKS VMSS
          * Apply the storage class
          * Create kv namespace
          * Apply flex vol installer
          * Fetch latest `atat` image from {{ tf_app_env_outputs.container_registry_name.value }}
          * Extract latest tag
          * Fetch latest `nginx` image from {{ tf_app_env_outputs.container_registry_name.value }}
          * Extract latest nginx tag
          * Apply the rest of the Kubernetes config for the site
          * Obtain IP addresses
      * **else**
        * [create k8s overlays](../ansible/roles/k8s/tasks/generate_overlays.yml)
          * Create template output directory
          * Interpolate the templates
        * [push overlays to storage bucket](../ansible/roles/k8s/tasks/push_overlays.yml)
          * Compress overlays
          * push overlays to a storage account
        * [configure the cluster](../ansible/roles/k8s/tasks/configure_public_cluster.yml)
          * Connect to the {{ namespace }} kubernetes cluster
          * Create {{ namespace }} namespace
          * "Attach the ACR to the K8s cluster"
          * Assign Network Contributor role to the AKS Service Principal for the Virtual Network
          * Get vmss
          * Assign the Vault Reader identity to the AKS VMSS
          * Apply the storage class
          * Create kv namespace
          * Apply flex vol installer
          * Fetch latest `atat` image from {{ tf_app_env_outputs.container_registry_name.value }}
          * Extract latest tag
          * Fetch latest `nginx` image from {{ tf_app_env_outputs.container_registry_name.value }}
          * Extract latest nginx tag
          * Apply the rest of the Kubernetes config for the site
          * Obtain IP addresses

<div style="page-break-after: always"></div>

```mermaid
graph TD
  subgraph circleci1
    CircleCI::deploy-atat::checkout --> CircleCI::deploy-atat::setup_remote_docker --> CircleCI::deploy-atat::install_azure_cli --> CircleCI::deploy-atat::log_into_ops_registry --> CircleCI::deploy-atat::docker_build --> CircleCI::deploy-atat::tag/push --> CircleCI::deploy-atat::run_container_image
  end

  subgraph ContainerInstance1
    CircleCI::deploy-atat::run_container_image --> Ansible::Infra::Crypto::gen_diffie_hellman --> Ansible::Infra::Bootstrap::fetch_atatpem --> Ansible::Infra::Bootstrap::fetch_bootstrap_vars --> Ansible::Infra::Bootstrap::deploy_bootstrap_env --> Ansible::Infra::Bootstrap::push_local_state_to_remote
  end

  subgraph circleci2
  Ansible::Infra::Bootstrap::push_local_state_to_remote --> Ansible::Infra::CircleCi::run_circle_ci_ops_build --> CircleCI::push-ops-image::docker_build --> CircleCI::push-ops-image::push_ops_image
  end

  subgraph ContainerInstance1
  CircleCI::push-ops-image::push_ops_image --> Ansible::Infra::CircleCi::Fetch_latest_ops_image_from --> Ansible::Infra::Terraform::get_backend_config --> Ansible::Infra::Terraform::deploy_application_env --> Ansible::Infra::Terraform::tf_apply_no_modules
  end

  subgraph circleci3
    Ansible::Infra::Terraform::tf_apply_no_modules --> Ansible::Infra::CircleCi::run_circle_ci_app_build --> CircleCI::push-app-image::docker_build --> CircleCI::push-app-image::push_ops_image
  end

  subgraph ContainerInstance1
    CircleCI::push-app-image::push_ops_image --> Ansible::Infra::AzureKeyvault::source_the_secrets --> Ansible::Infra::AzureKeyvault::bootstrap_keyvault_with_terraform_vars --> Ansible::Infra::AzureKeyvault::store_secrets_as_play_key=value --> Ansible::Infra::AzureKeyvault::secrets_to_json_file --> Ansible::Infra::AzureKeyvault::wipe_secrets --> Ansible::Databases::DB::source_ccpo_users_file --> Ansible::Databases::DB::provision_postgres --> Ansible::Databases::DB::grab_the_root_cert_from_yaml --> Ansible::Databases::DB::set_cert_fact --> Ansible::Databases::DB::write_cert_to_temp_file --> Ansible::Databases::DB::Create_or_update_PostgreSQL_Database --> Ansible::Databases::DB::Adds_uuid-ossp_extension_to_the_database --> Ansible::Databases::DB::Create_database_user --> Ansible::Databases::DB::Initialize_database --> Ansible::Databases::DB::Add_CCPO_users --> Ansible::k8s::Bootstrap::fetch_atatpem --> Ansible::k8s::Bootstrap::fetch_bootstrap_vars --> Ansible::k8s::Bootstrap::fetch_bootstrap_state --> Ansible::k8s::Terraform::get_backend_config --> Ansible::k8s::Terraform::get_variables --> Ansible::k8s::create_k8s_overlays --> Ansible::k8s::push_overlays_to_storage_bucket --> Ansible::k8s::k8s::configure_the_private_cluster
end

```
