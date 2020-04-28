# Intro

Ansible is a widely used, first class config as code tool. Its an idempotent, stateless way to make source controlled, declaritive, repeatable changes to config. yay.


## Requirements

* Python 3.7
* pip
* ansible

## Usage

I won't recreate the docs, but an example ansible run of something that affects config/runs a playbook looks like:

`ansible-playbook --extra-vars "var_1='val1' ... var_2='val2'" [OPTIONS] play.yml` 
