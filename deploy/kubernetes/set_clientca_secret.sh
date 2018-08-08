#!/bin/bash

kubectl -n atat delete secret atst-config-ini
kubectl -n atat create secret generic nginx-client-ca-bundle --from-file="${1}"
