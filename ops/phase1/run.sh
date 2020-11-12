#!/bin/bash
set -x
set -e

# if [ -z ${$1+x} ]; then echo "var is unset"; exit 1; else echo "var is set to '$1'"; fi
# wget https://releases.hashicorp.com/terraform/0.13.5/terraform_0.13.5_linux_amd64.zip
# unzip terraform_0.13.5_linux_amd64.zip
# mv -f terraform /usr/local/bin
[ ! -f service_principal.json ] && ./create-service-principle.sh
sp=$(cat service_principal.json)

echo "exporting terraform creds"
export ARM_CLIENT_ID=$(echo $sp | jq -r '.appId')
export ARM_CLIENT_SECRET=$(echo $sp | jq -r '.password')
export ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv)
export ARM_TENANT_ID=$(echo $sp | jq -r '.tenant')
export TF_VAR_operator_subscription_id=$ARM_SUBSCRIPTION_ID
export TF_VAR_operator_client_id=$ARM_CLIENT_ID
export TF_VAR_operator_client_secret=$ARM_CLIENT_SECRET
export TF_VAR_operator_tenant_id=$ARM_TENANT_ID

echo "ARM_CLIENT_ID=$ARM_CLIENT_ID"
echo "ARM_CLIENT_SECRET=$ARM_CLIENT_SECRET"
echo "ARM_SUBSCRIPTION_ID=$ARM_SUBSCRIPTION_ID"
echo "ARM_TENANT_ID=$ARM_TENANT_ID"
echo "-----------"
echo $TF_VAR_operator_subscription_id
echo $TF_VAR_operator_client_id
echo $TF_VAR_operator_client_secret
echo $TF_VAR_operator_tenant_id

echo "Terraform Bootstrap New Tenant"
cd ../../terraform/providers/bootstrap
terraform init
terraform plan -var "namespace=$1" -out out.plan .
terraform apply out.plan
echo "Now copying this state to the remote"
terraform init -force-copy


export REGISTRY_NAME=$(terraform output operations_container_registry_login_server)
export TF_VAR_resource_group_name=$(terraform output operations_resource_group_name)
export TF_VAR_storage_account_name=$(terraform output operations_storage_account_name)
export SUBNET_ID=$(terraform output operations_deployment_subnet_id)
export OPERATIONS_VIRTUAL_NETWORK=$(terraform output operations_virtual_network)
# Now, need to lock that folder down to just the subnet that was created.
az storage account update --resource-group ${TF_VAR_resource_group_name} --name ${TF_VAR_storage_account_name} --default-action Deny
az storage account network-rule add --resource-group ${TF_VAR_resource_group_name} --account-name ${TF_VAR_storage_account_name} --subnet ${SUBNET_ID}

echo "Building RHEL"
cd ../../../ops/phase1

cd ../../../atat-rhel-image
make run-build-push-task

echo "Building Python Base"
cd ../atst
az acr build --registry ${REGISTRY_NAME} \
  --build-arg IMAGE=${REGISTRY_NAME}/rhelubi:8.3 \
  --build-arg "redhat_username=$2" \
  --build-arg "redhat_password=$3" \
  --image rhel-py \
  --file python.Dockerfile \
  .

echo "Build Ops Dockerfile"
export COMMIT_SHA=$(git rev-parse HEAD)
az acr build --registry ${REGISTRY_NAME} \
  --build-arg IMAGE=${REGISTRY_NAME}/rhel-py:latest \
  --image ops:${COMMIT_SHA} \
  --file ops.Dockerfile \
  .

az container create \
  --resource-group ${TF_VAR_resource_group_name} \
  --name "$1-provisioner" \
  --ip-address Private \
  --vnet ${OPERATIONS_VIRTUAL_NETWORK} \
  --subnet deployment-subnet \
  --image ${REGISTRY_NAME}/ops:${COMMIT_SHA} \
  --registry-password ${TF_VAR_operator_client_secret} \
  --registry-username ${TF_VAR_operator_client_id} \
  --memory 4 \
  --cpu 4 \
  --secure-environment-variables "TF_VAR_resource_group_name=$TF_VAR_resource_group_name" "TF_VAR_storage_account_name=$TF_VAR_storage_account_name" "TF_VAR_operator_subscription_id=$TF_VAR_operator_subscription_id" "TF_VAR_operator_client_id=$TF_VAR_operator_client_id" "TF_VAR_operator_client_secret=$TF_VAR_operator_client_secret" "TF_VAR_operator_tenant_id=$TF_VAR_operator_tenant_id" \
  --restart-policy Never
