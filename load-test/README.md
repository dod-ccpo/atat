# Load Testing

We're using [Locust.io](https://locust.io/) for our load tests. The tests can be run locally or in a VM.

## Available Option (Env Vars)

`TARGET_URL` - The host address that locust should load test against
* If you're running the app locally http://docker.for.mac.localhost:8000
  * This is for running on a mac, you may need to use other methods to get the container to communicate with localhost on other systems
* Staging - https://staging.atat.dev
* Prod - https://master.atat.dev

`DISABLE_VERIFY` - False by default, set to true to prevent SSL verification

`ATAT_BA_USERNAME` + `ATAT_BA_PASSWORD` - Username and password for the basic auth on the staging and production sites

## To Run Locally
1. Build the docker container:

    `docker build . -t pwatat.azurecr.io/loadtest/locust`
2. Run the container:

    `
    docker run --rm -p 8089:8089 \
    -e TARGET_URL=https://master.atat.dev \
    -e DISABLE_VERIFY=false \
    -e ATAT_BA_USERNAME=<username> \
    -e ATAT_BA_PASSWORD=<password> \
    --name locust pwatat.azurecr.io/loadtest/locust:latest
    `

## To Update Image
1. Build the docker container:

    `docker build . -t pwatat.azurecr.io/loadtest/locust`
2. Push to our container registry

    `docker push pwatat.azurecr.io/loadtest/locust`

   * If you get an authorization failed message, you may need to re-authorize with this command first:

        `az acr login --name pwatat`
3. Restart the `atat-load-test` app service in the azure portal
   * Note the load test service is running on a free tier VM, so it will likely be paused. Start it up and press restart to referesh before beginning your load testing.
