#!/bin/bash

poetry build
cp ../../dist/atat-0.1.0.tar.gz .
func azure functionapp publish atat-serverless-test -i -b remote --build-native-dependencies