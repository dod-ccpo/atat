#!/bin/bash

export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

TF_DIR=/Users/michaelpapetti/Developer/atst/terraform/providers/bootstrap
SUBSCRIPTION_SECRET='GHACoKBg-F.kdC1POQZwemW7LZZfCkasZ2'
SUBSCRIPTION_CID='d805bb04-8589-49dc-9ea1-6d2678bcba0a'
SUBSCRIPTION_TENANT='b5ab0e1e-09f8-4258-afb7-fb17654bc5b3'
SUBSCRIPTION_ID='a0f587a4-2876-498d-a3d3-046cd98d5363'


cd $TF_DIR && terraform init
cd -

cd ../
poetry install
cd -
poetry install
SUBSCRIPTION_ID='a0f587a4-2876-498d-a3d3-046cd98d5363' SUBSCRIPTION_TENANT='b5ab0e1e-09f8-4258-afb7-fb17654bc5b3' SUBSCRIPTION_CID='d805bb04-8589-49dc-9ea1-6d2678bcba0a' SUBSCRIPTION_SECRET='GHACoKBg-F.kdC1POQZwemW7LZZfCkasZ2' poetry run ansible-playbook site.yml --extra-vars "tfvars_file_path=/Users/michaelpapetti/Developer/autoamted_atat_tf_ansible/terraform/providers/bootstrap/dryrun.tfvars
az_environment=dryrun2
app_name=atat
scripts_dir=/Users/michaelpapetti/Developer/atst/script
init_tf=yes
bootstrap_init_tf=yes
show_app_env_outputs=true
tf_base_dir=/Users/michaelpapetti/Developer/atst/terraform/providers
bootstrap_subscription_id='$SUBSCRIPTION_ID'
application_subscription_id='$SUBSCRIPTION_ID'
deploy_tag=v0.1.0"

#cd $TF_DIR && terraform show plan.tfplan
