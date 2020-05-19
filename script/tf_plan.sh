#!/bin/bash

export PATH="$HOME/.poetry/bin:$PATH"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
eval "$(pyenv virtualenv-init -)"

export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"


<<<<<<< HEAD

=======
>>>>>>> fixes spacing err, changes dir
if [ -z "$DEPLOY_TAG" ] || [ -z "$TF_DIR" ] || [ -z "$VAULT_SECRET" ] || [ -z "$VAULT_URL" ] || [ -z "$VAULT_CLIENT_ID" ] ||  [ -z "$VAULT_TENANT" ] ||  [ -z "$SUBSCRIPTION_ID" ]
then
echo "Set DEPLOY_TAG, TF_DIR, VAULT_SECRET, VAULT_CLIENT_ID, VAULT_TENANT, SUBSCRIPTION_ID"
exit 1;
fi
<<<<<<< HEAD
cd $TF_DIR && terraform init
cd ../../../ansible
=======

cd ../ansible
>>>>>>> fixes spacing err, changes dir
poetry run ansible-playbook ../ansible/site.yml --extra-vars "provision_pwdev=true deploy_tag=$DEPLOY_TAG tf_dir='$TF_DIR' vault_url='$VAULT_URL' vault_secret='$VAULT_SECRET' vault_client_id='$VAULT_CLIENT_ID' vault_tenant='$VAULT_TENANT' vault_subscription_id='$SUBSCRIPTION_ID'"
cd $TF_DIR && terraform show $TF_DIR/plan.tfplan
