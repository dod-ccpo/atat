#!/bin/bash

ENVIRONMENT=$1
echo "Prompt for user login"
az login

echo "Setting variables..."
AKS_INFO=$(az aks show -n cloudzero-${ENVIRONMENT}-k8s -g cloudzero-${ENVIRONMENT}-vpc)
AKS_SP_CLIENT_ID=$(echo $AKS_INFO | jq -r .servicePrincipalProfile.clientId)
AKS_NODE_RESOURCE_GROUP=$(echo $AKS_INFO | jq -r .nodeResourceGroup)
AKS_VMSS_NAME=$(az vmss list -g $AKS_NODE_RESOURCE_GROUP | jq -r .[0].name)
VAULT_READER_ID=$(az identity show -n cloudzero-${ENVIRONMENT}-cloudzero-${ENVIRONMENT}-vault-reader -g cloudzero-${ENVIRONMENT}-cloudzero-${ENVIRONMENT}-vault-reader | jq -r .id)
VNET_ID=$(az network vnet show -g cloudzero-${ENVIRONMENT}-vpc -n cloudzero-${ENVIRONMENT}-network | jq -r .id)

echo "Attach the ACR to the K8s cluster"
az aks update -n cloudzero-${ENVIRONMENT}-k8s -g cloudzero-${ENVIRONMENT}-vpc --attach-acr cloudzero${ENVIRONMENT}registry

echo "Assign Network Contributor role to the AKS Service Principal for the Virtual Network"
az role assignment create --role "Network Contributor" --assignee $AKS_SP_CLIENT_ID --scope $VNET_ID

echo "Assign the Vault Reader identity to the AKS VMSS"
az vmss identity assign -g $AKS_NODE_RESOURCE_GROUP -n $AKS_VMSS_NAME --identities $VAULT_READER_ID
