# Load Testing

We're using [Locust.io](https://locust.io/) for our load tests. The tests can be run locally or in a VM.

## Available Option (Env Vars)

`TARGET_URL` - The host address that locust should load test against

- If you're running the app locally http://docker.for.mac.localhost:8000
  - This is for running on a mac, you may need to use other methods to get the container to communicate with localhost on other systems
- Staging - https://staging.atat.dev
- Prod - https://master.atat.dev

`DISABLE_VERIFY` - False by default, set to true to prevent SSL verification

`ATAT_BA_USERNAME` + `ATAT_BA_PASSWORD` - Username and password for the basic auth on the staging and production sites

## To Run Locally

1. Build the docker container:

   `docker build . -t loadtest/locust`

2. Run the container:

   `docker run --rm -p 8089:8089 -e TARGET_URL=https://master.atat.dev -e DISABLE_VERIFY=false -e ATAT_BA_USERNAME=<username> -e ATAT_BA_PASSWORD=<password> --name locust loadtest/locust:latest`
