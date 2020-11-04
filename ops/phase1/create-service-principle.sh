#! /bin/bash
set -x
set -e

# How do you find these GUIDs?
#
# Coutesy of Jeff Deville, you can watch your `Network` tab for whichever
# browser's developer tools you're using. There will be a PATCH request.
# The `resourceAppId` will be the `--api` field. The `resourceAccess` ids
# wil be he `--api-permissions values`.
sp=$(az ad sp create-for-rbac)
appId=$(echo $sp | jq .appId | tr -d '"')
subscription_id=$(az account show --query id --output tsv)
objectId=$(az ad sp show --id $appId --query "objectId" --output tsv)
AzureADGraphID=$(az ad sp show --id 00000002-0000-0000-c000-000000000000 --query "objectId" --output tsv)
MSGraphID=$(az ad sp show --id 00000003-0000-0000-c000-000000000000 --query "objectId" --output tsv)
az role assignment create --assignee $appId --role "User Access Administrator" --subscription $subscription_id

az rest --method POST \
        --uri https://graph.microsoft.com/v1.0/servicePrincipals/$objectId/appRoleAssignments \
        --body "{
          'principalId': '$objectId',
          'resourceId': '$AzureADGraphID',
          'appRoleId': '1cda74f2-2616-4834-b122-5cb1b07f8a59'
        }"
az rest --method POST \
        --uri https://graph.microsoft.com/v1.0/servicePrincipals/$objectId/appRoleAssignments \
        --body "{
          'principalId': '$objectId',
          'resourceId': '$AzureADGraphID',
          'appRoleId': '824c81eb-e3f8-4ee6-8f6d-de7f50d565b7'
        }"
az rest --method POST \
        --uri https://graph.microsoft.com/v1.0/servicePrincipals/$objectId/appRoleAssignments \
        --body "{
          'principalId': '$objectId',
          'resourceId': '$AzureADGraphID',
          'appRoleId': '78c8a3c8-a07e-4b9e-af1b-b5ccab50a175'
        }"
az rest --method POST \
        --uri https://graph.microsoft.com/v1.0/servicePrincipals/$objectId/appRoleAssignments \
        --body "{
          'principalId': '$objectId',
          'resourceId': '$MSGraphID',
          'appRoleId': '1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9'
        }"

sleep 10

az ad app permission grant --id $appId \
  --api 00000002-0000-0000-c000-000000000000 \
  --scope "Directory.ReadWrite.All Directory.AccessAsUser.All User.Read User.Read.All"
az ad app permission grant --id $appId \
  --api cfa8b339-82a2-471a-a3c9-0fc0be7a4093 \
  --scope "user_impersonation"
az ad app permission grant --id $appId \
  --api e406a681-f3d4-42a8-90b6-c2b029497af1 \
  --scope "user_impersonation"
az ad app permission grant --id $appId \
  --api 00000003-0000-0000-c000-000000000000 \
  --scope "Application.ReadWrite.All User.Read"
az ad app permission grant --id $appId \
  --api $appId \
  --scope "user_impersonation"


echo $sp | jq '.'
echo $sp  > service_principal.json

sleep 10
