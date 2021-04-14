## BrowserStack README

## UI Test Automation

ATAT uses [BrowserStack](https://www.Browserstack.com/), a testing PaaS
for UI test automation and as a form of integration testing.

These tests do not run locally as part of the regular test suite.

Tests are created using PyTest and Python and then executed from the command line interface through BrowserStack.
We update these tests/steps regularly, and they can be found within the `uitests` directory.


## Testing philosophy

The tests have been created to traverse the most common user flows in ATAT. There are a few tests (e.g. "New Portfolio - no optional fields")
that check for regressions. Others (e.g. "Remove Portfolio Member") check less-common, "negative path" flows. Tests are added as necessary
to ensure fairly thorough review of ATAT.

## Setting up for Running BrowserStack tests

To run BrowserStack tests against a local instance of ATAT, you will need the following:

- Download [ngrok](https://ngrok.com/)
- NGROK_TOKEN - personal ngrok token.
- BROWSERSTACK_API_KEY - personal BrowserStack token
- In terminal:
    - `scripts/create_local_certs`
    - `poetry shell`
    - `git pull`
    - `service redis-server start`
    - `service postgresql start`
    - `pyenv shell 3.8.8`
    - `pip install --upgrade pip`
    - `pip install poetry`
    - `script/setup`
    - `script/secure_server`

NGROK TUNNEL
From the ngrok application you will need to key your ngrok token: `ngrok authtoken xyz`
- Your token is then entered in the ngrok terminal, click enter
- Then enter `ngrok http https://localhost:8000`
- Your ngrok forwarding addresses are listed in the ngrok terminal

SETTING YOUR ENVIRONMENT VARIABLES
- In terminal:
    - `export baseUrl="<target url to test>"`
    - `export loginUrl="<target url to test for auto login>"`
    - `export browserStackApi="https://<username>:<accesskey>@hub-cloud.browserstack.com/wd/hub"`

## Running a test

```
 # running the test local script alone the default configuration
 (.venv) $ pytest -s -v uitests/framework/test_cases/test_login.py
```

*Running test local*:

 ```
 # running the test local script alone with the local chrome drivers. 
 (.venv) $ pytest -s -v uitests/framework/test_cases/test_login.py --browser chrome-local
 ```

NOTE: for be able to run this test local we need to install the drivers in our system,  
and it required to be the same version that the browser we have on it.

to install the drivers follow the [Selenium Documentation](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference),


*Running test with browserstack*:

 ```
 # running a single test script with the BrowserStack's Edge driver. 
 (.venv) $ pytest -s -v uitests/framework/test_cases/test_login.py --browser edge
 # running a single test script alone the BrowserStack's ie driver. 
 (.venv) $ pytest -s -v uitests/framework/test_cases/test_login.py --browser ie
  # running a single test script alone the BrowserStack's chrome driver. 
 (.venv) $ pytest -s -v uitests/framework/test_cases/test_login.py --browser chrome
 ```
*Running multiples script on one command*:

We are using markers for running a collection of script for example the marker "smoke",
Contains various scripts that more common use for calling the market we use the fla "-m".
Ex.:

 ```
 # Running multiple tests marks as smoke with the BrowserStack's chrome drivers. 
 (.venv) $ pytest -s -v -m smoke uitests/* --browser chrome
 ```

*Running in parallel*

We do this with the flag "-n" or limit will be 7 on our current contract with
BrowserStack that can change on time so verify with your provider. Ex.:

```
# Running a test with the BrowserStack's chrome drivers in parallel. 
 (.venv) $ pytest -n=2 -s -v -m smoke uitests/* --browser chrome
```

Note: might no work on mac