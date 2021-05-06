# ATAT UI Tests

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

To run the BrowserStack tests locally, you will need the `BrowserStackLocal` command line tool as well as to set several environment
variables. When running the tests against a deployed environment, only certain environment variables are required.

To get started, you will need your BrowserStack API token, available from the BrowserStack Automate console. This will be referred to
as `<BROWSERSTACK_ACCESS_KEY>` throughout this section.

### Local Testing

To run the tests against a local server, you will need to install the `BrowserStackLocal` command line tool, which can be
downloaded from the
[BrowserStack documentation](https://www.browserstack.com/local-testing/automate#:~:text=for%20more%20details-,Via%20command-line%20interface,-%3A).
For Linux, choose the "Linux 64-bit" option. Unzip the file, and place the binary somewhere on your PATH (for example `/usr/local/bin` on Linux).

Start the BrowserStackLocal server by running:

```
BrowserStackLocal --key <BROWSERSTACK_ACCESS_KEY>
```

Keep that command running and open a new terminal window, where you can start the local ATAT server. This can be done by
running the following commands in the ATAT repo:

```
export FLASK_ENV=development
scripts/create_local_certs
git pull
sudo service redis-server start
sudo service postgresql start
poetry shell
script/setup
python script/seed_sample.py
script/secure_server
```

### Setting Environment Variables

In another terminal session, where the tests will be run, there are several additional environment variables that will need to
be set in order to successfully run the test suite. Start by running `poetry shell` and then `export` the following environment variables:

| Environment Variable Name | Description                                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| `BROWSERSTACK_BUILD_NAME` | The build name to use in BrowserStack                                                                  |
| `BROWSERSTACK_USERNAME`   | Your username to use when interacting with BrowserStack Automate, found in the console                 |
| `BROWSERSTACK_ACCESS_KEY` | The same API key identified earlier                                                                    |
| `baseUrl`                 | The root URL where the ATAT application is deployed (such as `https://localhost:8000` for local tests) |
| `loginUrl`                | The full URL for the login endpoint the tests should use to authenticate to the application            |

## Running the tests

The following items can be configured when running the test suite, each configured with different command line options to the `pytest`
invocation.

Generally, the expected command line structure is:

```
pytest -s -v [-m <TEST_MARKERS>] <TEST_FILES> --browser <BROWSER> --run-type <RUN_TYPE>
```

Each of these are explained further.

### Test Markers

The UI tests are grouped by various `pytest` markers, which allow subsets of the tests to be run. Some examples are the `smoke` or
`regression` markers. These are defined in the `pytest.ini` file.

### Test Files

This can either be a single argument with a directory, a file containing tests, or many files or directory as different arguments.
Generally though, it will either be the `uitests/` directory as a whole, or a specific file with the test that you want to run,
such as `uitests/framework/test_cases/test_login.py`.

### Browser

This should specify the browser to use. The specific browsers that may work are defined  in the
`uitests/framework/test_cases/conftest.py` file; however, the following are the supported values:

 - `chrome` to run the tests using the latest version of Google Chrome on Windows 10
 - `edge` to run the tests using the latest version of Microsoft Edge on Windows 10
 - `ie` to run the tests using IE 11 on Windows 10

### Run Type

This option defines whether the tests should run entirely locally, without interacting with BrowserStack at all; whether the
tests should use the `BrowserStackLocal` interface (configured in the "Local Testing" section above); or whether the tests should
use BrowserStack Automate API directly (supported only for internet-accessible websites). The valid values are, respecively `Local`,
`BrowserStackLocal`, or `BrowserStackRemote`.

In general, using the `BrowserStackLocal` or `BrowserStackRemote` is preferred and what these tests are geared towards.

### Example Invocations

To invoke the smoke tests in Chrome against the BrowserStackLocal server (assuming it was already started), run:

```
pytest -s -v -m smoke uitests/* --no-cov --browser chrome --run-type BrowserStackLocal
```

To invoke all tests in edge against a live environment (assuming the environment variables are correctly set), run:

```
pytest -s -v uitests/* --no-cov --browser edge --run-type BrowserStackRemote
```

To invoke several sequential runs of the smoke tests, for each browser, against the local server:

```
pytest -s -v -m smoke uitests/* --no-cov --browser chrome --run-type BrowserStackLocal
pytest -s -v -m smoke uitests/* --no-cov --browser edge --run-type BrowserStackLocal
pytest -s -v -m smoke uitests/* --no-cov --browser ie --run-type BrowserStackLocal
```
