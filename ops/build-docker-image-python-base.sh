#! /bin/bash

env DOCKER_BUILDKIT=1 docker build \
    -t atst:rhel-py \
    -f python.Dockerfile \
    --build-arg IMAGE=$CONTAINER_REGISTRY/rhelubi:8.3 \
    --secret id=redhat_username,src=redhat_username.secret \
    --secret id=redhat_password,src=redhat_password.secret \
    .
