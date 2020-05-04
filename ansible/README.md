# Intro

Ansible is a widely used, first class, config as code tool. Its an idempotent, stateless way to make source controlled, declarative, repeatable changes to config. yay.

To use ansible, the operator codes out his actions and applies them, like terraform, to a set of hosts, or subset of hosts.  We logically group reusable actions into `roles`,`plays`,`tasks` and then call them at the command line with variable values in the common places (env, file, cmd line args).

This is especially useful in unattended scenarios controlled by change management, source control and a task runner like AWX or CI/CD.  Security benefits include secrets/config at runtime.

Even though ATAT is completely containerized, its not immune to the benefits of ansible.  Providing a completely decoupled abstraction layer to Terraform increases its operationlization by giving us the ability to store configuration in an encrypted cloud store and enabling unattended, batch/scheduled execution of TF to stay continually compliant, avoiding drift and correcting manual changes to environments.



## Requirements

* Python 3.7
* pip or poetry
* ansible

## Usage Example

I won't recreate the docs, but an example ansible run of something that affects config/runs a playbook looks like:

`ansible-playbook play.yml --extra-vars "var_1='val1' ... var_2='val2'" [OPTIONS]`


## General Use Case Examples

Classically, ops engineers write imperative scripts to carry out tasks, for example:

```
#!/bin/bash
mkdir ./some_dir

```

This is hard to execute at scale and there's no guarantee the command will succeed.

In ansible, as part of a play for a larger config, called a `role` the command can be assigned to all or a subset of hosts across an entire estate.
```
- name: Create a directory if it does not exist
  file:
    path: /etc/some_directory
    state: directory
    mode: '0755'
```


## A more specific use case

### Bridging the gap between developing terraform and operationlizing it.

A human has to be involved at some point when writing terraform. Lets say you're adding a new variable and value to an existing TF like:

```
variables.tf:

variable new_vaccines {

  type= list
  value = ['x-10','y-123','zz-top']
}

```

In our set of ansible, there's a task in the azure role that will parse variables.tf for values and atomically add them to the keyvault. To do that you'd perform the following:

`ansible-playbook site.yml --extra-vars "bootstrap_terraform=true deploy_tag='v0.0.1' tf_dir='/path/to/terraform/providers/pwdev' vault_url='some_vault_url' vault_secret='some_secret' vault_client_id='some_client_id' vault_tenant='some_tenant'" `


If I want to refresh the local variables.tf file, there's another task that will pull variables from key vault and populate a json file. You can manually port the returned json to HCL if you'd like but the idea is that machines run terraform in production, hence json. To retrieve the current variable values:


`ansible-playbook site.yml --extra-vars "ops=true secrets_to_file=true deploy_tag='v0.0.1' tf_dir='/path/to/terraform/' vault_url='some_url' vault_secret='some_secret' vault_client_id='some_client_id' vault_tenant='some_tenant' vault_subscription_id='some_subscription'"`

In out case, secrets achieve vault and csp agnostic versions by storing all terraform config under the key `deploy_tag`, this way we can tie terraform releases to their respective secrets and have repeatable deployments.

There are lots more possibilities and i will be adding here in the future.

## Links

[Ansible Documentation](https://docs.ansible.com/ansible/latest/user_guide/intro_getting_started.html)
## Future Considerations

Is ATAT able to leverage tenant creation via TF and ansible over API calls to the API directly?
