#!/bin/bash



if [ -z "$DEPLOY_TAG" ] || [ -z "$TF_DIR" ] || [ -z "$VAULT_SECRET" ] || [ -z "$VAULT_URL" ] || [ -z "$VAULT_CLIENT_ID" ] ||  [ -z "$VAULT_TENANT" ] ||  [ -z "$SUBSCRIPTION_ID" ]
then
echo "Set DEPLOY_TAG, TF_DIR, VAULT_SECRET, VAULT_CLIENT_ID, VAULT_TENANT, SUBSCRIPTION_ID"
exit 1;
fi
cd $TF_DIR && terraform init
cd ../../../ansible
poetry run ansible-playbook ../ansible/site.yml --extra-vars "provision_pwdev=true deploy_tag=$DEPLOY_TAG tf_dir='$TF_DIR' vault_url='$VAULT_URL' vault_secret='$VAULT_SECRET' vault_client_id='$VAULT_CLIENT_ID' vault_tenant='$VAULT_TENANT' vault_subscription_id='$SUBSCRIPTION_ID'"
cd $TF_DIR && terraform show $TF_DIR/plan.tfplan









