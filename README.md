# ATAT

[![Build Status](https://circleci.com/gh/dod-ccpo/atat.svg?style=svg)](https://circleci.com/gh/dod-ccpo/atat)

## Description

This is the user-facing web application for ATAT.

## Installation

### System Requirements
ATAT uses the [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all)
pattern for setting up and running the project. The scripts are located in the
`script` directory and use script fragments in the
[scriptz](https://github.com/dod-ccpo/scriptz) repository that are shared across
ATAT repositories.

Before running the setup scripts, a couple of dependencies need to be installed
locally:

* `python` == 3.7.3
  Python version 3.7.3 **must** be installed on your machine before installing `pipenv`.
  You can download Python 3.7.3 [from python.org](https://www.python.org/downloads/)
  or use your preferred system package manager. Multiple versions of Python can exist on one
  computer, but 3.7.3 is required for ATAT.

* `pipenv`
  ATAT requires `pipenv` to be installed for python dependency management. `pipenv`
  will create the virtual environment that the app requires. [See
  `pipenv`'s documentation for instructions on installing `pipenv`](
  https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv).

* `yarn`
  ATAT requires `yarn` for installing and managing Javascript
  dependencies: https://yarnpkg.com/en/

* `postgres` >= 9.6
  ATAT requires a PostgreSQL instance (>= 9.6) for persistence. Have PostgresSQL installed
  and running on the default port of 5432. (A good resource for installing and running
  PostgreSQL for Macs is [Postgres.app](https://postgresapp.com/). Follow the instructions,
  including the optional Step 3, and add `/Applications/Postgres.app/Contents/Versions/latest/bin`
  to your `PATH` environment variable.) You can verify that PostgresSQL is running
  by executing `psql` and ensuring that a connection is successfully made.

* `redis`
  ATAT also requires a Redis instance for session management. Have Redis installed and
  running on the default port of 6379. You can ensure that Redis is running by
  executing `redis-cli` with no options and ensuring a connection is succesfully made.

* [`entr`](http://eradman.com/entrproject/)
  This dependency is optional. If present, the queue worker process will hot
  reload in development.

### Cloning
This project contains git submodules. Here is an example clone command that will
automatically initialize and update those modules:

    git clone --recurse-submodules git@github.com:dod-ccpo/atat.git

If you have an existing clone that does not yet contain the submodules, you can
set them up with the following command:

    git submodule update --init --recursive

### Setup
This application uses Pipenv to manage Python dependencies and a virtual
environment. Instead of the classic `requirements.txt` file, pipenv uses a
Pipfile and Pipfile.lock, making it more similar to other modern package managers
like yarn or mix.

To perform the installation, run the setup script:

    script/setup

The setup script creates the virtual environment, and then calls script/bootstrap
to install all of the Python and Node dependencies and run database migrations.

To enter the virtualenv manually (a la `source .venv/bin/activate`):

    pipenv shell

If you want to automatically load the virtual environment whenever you enter the
project directory, take a look at [direnv](https://direnv.net/).  An `.envrc`
file is included in this repository.  direnv will activate and deactivate
virtualenvs for you when you enter and leave the directory.

### Troubleshooting Setup

If you have a new postgres installation you might encounter
errors about the `postgres` role not existing. If so, run:

```
createuser -s postgres
```

If `script/setup` complains that the database does not exist,
run:

```
createdb atat
```

## Running (development)

To start the app locally in the foreground and watch for changes:

    script/server

After running `script/server`, the application is available at
[`http://localhost:8000`](http://localhost:8000).


### Users

There are currently six mock users for development:

- Sam (a CCPO)
- Amanda
- Brandon
- Christina
- Dominick
- Erica

To log in as one of them, navigate to `/login-dev?username=<lowercase name>`.
For example `/login-dev?username=amanda`.

In development mode, there is a `DEV Login` button available on the home page
that will automatically log you in as Amanda.

Additionally, this endpoint can be used to log into any real users in the dev environments by providing their DoD ID:
`/login-dev?dod_id=1234567890123`

When in development mode, you can create new users by passing first name, last name, and DoD ID query parameters to `/dev-new-user` like so:
```
/dev-new-user?first_name=Harrold&last_name=Henderson&dod_id=1234567890123
```
And it will create the new user, sign in as them, and load their profile page to fill out the rest of the details.

Once this user is created, you can log in as them again the future using the DoD ID dev login endpoint documented above.

### Seeding the database

We have a helper script that will seed the database with requests, portfolios and
applications for all of the test users:

`pipenv run python script/seed_sample.py`

### Email Notifications

To send email, the following configuration values must be set:

```
MAIL_SERVER = <SMTP server URL>
MAIL_PORT = <SMTP server port>
MAIL_SENDER = <Login name for the email account and sender address>
MAIL_PASSWORD = <login password for the email account>
MAIL_TLS = <Boolean, whether TLS should be enabled for outgoing email. Defaults to false.>
```

When the `DEBUG` environment variable is enabled and the app environment is not
set to production, sent email messages are available at the `/messages` endpoint.
Emails are not sent in development and test modes.

### File Uploads and Downloads

Testing file uploads and downloads locally requires a few configuration options.

In the flask config (`config/base.ini`, perhaps):

```
CSP=< azure | mock>

AZURE_STORAGE_KEY=""
AZURE_ACCOUNT_NAME=""
AZURE_TO_BUCKET_NAME=""
```

There are also some build-time configuration that are used by parcel. Add these to `.env.local`, and run `rm -r .cache/` before running `yarn build`:

```
CLOUD_PROVIDER=<azure | mock>
AZURE_ACCOUNT_NAME=""
AZURE_CONTAINER_NAME=""
```

## Testing

Tests require a test database:

```
createdb atat_test
```

To run lint, static analysis, and Python unit tests:

    script/test

To run only the Python unit tests:

    pipenv run python -m pytest

To re-run Python tests each time a file is changed:

    pipenv run ptw

This project also runs Javascript tests using jest. To run the Javascript tests:

    yarn test

To re-run the Javascript tests each time a file is changed:

    yarn test:watch

To generate coverage reports for the Javascript tests:

    yarn test:coverage

## Configuration

- `ASSETS_URL`: URL to host which serves static assets (such as a CDN).
- `AZURE_ACCOUNT_NAME`: The name for the Azure blob storage account
- `AZURE_BILLING_ACCOUNT_NAME`: The name for the root Azure billing account
- `AZURE_CALC_CLIENT_ID`: The client id used to generate a token for the Azure pricing calculator
- `AZURE_CALC_RESOURCE`: The resource URL used to generate a token for the Azure pricing calculator
- `AZURE_CALC_SECRET`: The secret key used to generate a token for the Azure pricing calculator
- `AZURE_CALC_URL`: The redirect URL for the Azure pricing calculator
- `AZURE_LOGIN_URL`: The URL used to login for an Azure instance.
- `AZURE_STORAGE_KEY`: A valid secret key for the Azure blob storage account
- `AZURE_TO_BUCKET_NAME`: The Azure blob storage container name for task order uploads
- `BLOB_STORAGE_URL`: URL to Azure blob storage container.
- `CAC_URL`: URL for the CAC authentication route.
- `CA_CHAIN`: Path to the CA chain file.
- `CDN_ORIGIN`: URL for the origin host for asset files.
- `CELERY_DEFAULT_QUEUE`: String specifying the name of the queue that background tasks will be added to.
- `CONTRACT_END_DATE`: String specifying the end date of the JEDI contract. Used for task order validation. Example: 2019-09-14
- `CONTRACT_START_DATE`: String specifying the start date of the JEDI contract. Used for task order validation. Example: 2019-09-14.
- `CRL_FAIL_OPEN`: Boolean specifying if expired CRLs should fail open, rather than closed.
- `CRL_STORAGE_CONTAINER`: Path to a directory where the CRL cache will be stored.
- `CSP`: String specifying the cloud service provider to use. Acceptable values: "azure", "mock", "mock-csp".
- `DEBUG`: Boolean. A truthy value enables Flask's debug mode. https://flask.palletsprojects.com/en/1.1.x/config/#DEBUG
- `DISABLE_CRL_CHECK`: Boolean specifying if CRL check should be bypassed. Useful for instances of the application container that are not serving HTTP requests, such as Celery workers.
- `ENVIRONMENT`: String specifying the current environment. Acceptable values: "dev", "prod".
- `LIMIT_CONCURRENT_SESSIONS`: Boolean specifying if users should be allowed only one active session at a time.
- `LOG_JSON`: Boolean specifying whether app should log in a json format.
- `MAIL_PASSWORD`: String. Password for the SMTP server.
- `MAIL_PORT`: Integer. Port to use on the SMTP server.
- `MAIL_SENDER`: String. Email address to send outgoing mail from.
- `MAIL_SERVER`: The SMTP host
- `MAIL_TLS`: Boolean. Use TLS to connect to the SMTP server.
- `MICROSOFT_TASK_ORDER_EMAIL_ADDRESS`: String. Email address for Microsoft to receive PDFs of new and updated task orders.
- `PERMANENT_SESSION_LIFETIME`: Integer specifying how many seconds a user's session can stay valid for. https://flask.palletsprojects.com/en/1.1.x/config/#PERMANENT_SESSION_LIFETIME
- `PGDATABASE`: String specifying the name of the postgres database.
- `PGHOST`: String specifying the hostname of the postgres database.
- `PGPASSWORD`: String specifying the password of the postgres database.
- `PGPORT`: Integer specifying the port number of the postgres database.
- `PGSSLMODE`: String specifying the ssl mode to use when connecting to the postgres database. https://www.postgresql.org/docs/9.1/libpq-ssl.html
- `PGSSLROOTCERT`: Path to the root SSL certificate for the postgres database.
- `PGUSER`: String specifying the username to use when connecting to the postgres database.
- `PORT`: Integer specifying the port to bind to when running the flask server. Used only for local development.
- `REDIS_URI`: URI for the redis server.
- `SECRET_KEY`: String key which will be used to sign the session cookie. Should be a long string of random bytes. https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
- `SERVER_NAME`: Hostname for ATAT. Only needs to be specified in contexts where the hostname cannot be inferred from the request, such as Celery workers. https://flask.palletsprojects.com/en/1.1.x/config/#SERVER_NAME
- `SESSION_COOKIE_NAME`: String value specifying the name to use for the session cookie. https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_NAME
- `SESSION_COOKIE_DOMAIN`: String value specifying the name to use for the session cookie. This should be set to the root domain so that it is valid for both the main site and the authentication subdomain. https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_DOMAIN
- `SESSION_KEY_PREFIX`: A prefix that is added before all session keys: https://pythonhosted.org/Flask-Session/#configuration
- `SESSION_TYPE`: String value specifying the cookie storage backend. https://pythonhosted.org/Flask-Session/
- `SESSION_COOKIE_SECURE`: https://flask.palletsprojects.com/en/1.1.x/config/#SESSION_COOKIE_SECURE
- `SESSION_USE_SIGNER`: Boolean value specifying if the cookie sid should be signed.
- `SQLALCHEMY_ECHO`: Boolean value specifying if SQLAlchemy should log queries to stdout.
- `STATIC_URL`: URL specifying where static assets are hosted.
- `USE_AUDIT_LOG`: Boolean value describing if ATAT should write to the audit log table in the database. Set to "false" by default for performance reasons.
- `WTF_CSRF_ENABLED`: Boolean value specifying if WTForms should protect against CSRF. Should be set to "true" unless running automated tests.

### UI Test Automation

AT-AT uses [Ghost Inpsector](https://app.ghostinspector.com/), a testing PaaS
for UI test automation and as a form of integration testing.
These tests do not run locally as part of the regular test suite,
but they do run in CI.

Ghost Inspector was developed to make it easier to create, maintain, and
execute UI tests than vanilla Selenium. Ghost Inspector tests and steps can
be exported to files that the Selenium IDE can import. We export these tests/steps
regularly and archive them with the AT-AT codebase in the `uitests` directory.

For further information about Ghost Inspector and its use in AT-AT, check out [its README](./uitests/README.md)
in the `uitests` directory.

## Notes

Jinja templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache


## Icons
To render an icon, use

```jinja
{% import "components/icon.html" %}
{{ Icon("icon-name", classes="css-classes") }}
```

where `icon-name` is the filename of an svg in `static/icons`.

All icons used should be from the Noun Project, specifically [this collection](https://thenounproject.com/monstercritic/collection/tinicons-a-set-of-tiny-icons-perfect-for-ui-elemen/) if possible.

SVG markup should be cleaned an minified, [Svgsus](http://www.svgs.us/) works well.

## Deployment

### Docker build

For testing the Docker build, the repo includes a `docker-compose.yml` that will run the app container with an NGINX server in front of it. To run it, you will need `docker` and `docker-compose` installed, then:

```
docker-compose up
```

The app will be available on http://localhost:8080.

The build assumes that you have redis and postgres running on their usual ports on your host machine; it does not pull images for those services. The docker-compose build is not suitable for development because it does not mount or reload working files.

### Dev login

The `/login-dev` endpoint is protected by HTTP basic auth when deployed. This can be configured for NGINX following the instructions [here](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/). The following config should added within the main server block for the site:

```nginx
location /login-dev {
    auth_basic "Developer Access";
    auth_basic_user_file /etc/apache2/.htpasswd;
    [proxy information should follow this]
}
```

The location block will require the same proxy pass configuration as other location blocks for the app.

## Secrets Detection

This project uses [detect-secrets](https://github.com/Yelp/detect-secrets) to help prevent secrets from being checked into source control. Secret detection is run automatically as part of `script/test` and can be run separately with `script/detect_secrets`.

If you need to check in a file that raises false positives from `detect-secrets`, you can add it to the whitelist. Run:

```
pipenv run detect-secrets scan --no-aws-key-scan --no-stripe-scan --no-slack-scan --no-artifactory-scan --update .secrets.baseline
```

and then:

```
pipenv run detect-secrets audit .secrets.baseline
```

The audit will open an interactive prompt where you can whitelist the file. This is useful if you're checking in an entire file that looks like or is a secret (like a sample PKI file).

Alternatively, you can add a `# pragma: allowlist secret` comment to the line that raised the false positive. See the [detect-secret](https://github.com/Yelp/detect-secrets#inline-allowlisting) docs for more information.

It's recommended that you add a pre-commit hook to invoke `script/detect_secrets`. Add the example below or something equivalent to `.git/hooks/pre-commit`:

```
#!/usr/bin/env bash

if ./script/detect_secrets staged; then
  echo "secrets check passed"
else
  echo -e "**SECRETS DETECTED**"
  exit 1
fi
```

Also note that if the line number of a previously whitelisted secret changes, the whitelist file, `.secrets.baseline`, will be updated and needs to be committed.

