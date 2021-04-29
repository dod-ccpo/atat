# Load Testing

We're using [Locust.io](https://locust.io/) for our load tests. The tests can be run locally or in a VM.

## Available Option (Env Vars)

`DISABLE_VERIFY` - False by default, set to true to prevent SSL verification if you're testing against self-signed certificates or other secure dev environments.

## To Run Locally

1. Build the docker container (from within the load-test folder):

   `docker build . -t locust`

2. Run the container (setting the host address such that it can be reached from the host OS):

   `docker run --rm -p 8089:8089 -e DISABLE_VERIFY=false locust:latest -H https://host.docker.internal:8000`
