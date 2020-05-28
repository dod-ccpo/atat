# Convenience Scripts

  Scripts to expedite workflows


## Inventory Notes


<<<<<<< HEAD
`tf_plan.sh`  

### Requires: 

* `terraform` 
* `ansible` 
* An azure account with keyvault credentials
* A known (currently semver) version of terraform infra config. This tag is the name of the azure secret holding relevant config values.

### Usage  

* Set your azure credentials in the env. 
* Set env var `TF_DIR` which points to where your terraform lives
* Set the `DEPLOY_TAG` to the semver version that correlates w/ the terraform you're executing 


### PR Review Use Case

* Follow the config steps above, the `deploy_tag` format is TBD but for now its based on semver.
* Run the script
* The result should not fail and you should be able to see the `plan.tfplan` output as a diff to what terraform would CRUD if applied.
* Compare the `plan.tfplan` output to the intended changes from the PR comments


