# Image source is provided using `--build-arg IMAGE=<some-image>`.
# This will typically be our RHEL Python image.
#
# --build-arg IMAGE=cloudzerodryrunregistry.azurecr.io/rhel-py
#
# https://docs.docker.com/engine/reference/commandline/build/#options
ARG IMAGE

# FROM $IMAGE as builder
FROM $IMAGE as builder

ARG CDN_URL=/static/assets/
ENV TZ UTC

WORKDIR /install

RUN yum updateinfo && \
      yum install -y \
      curl \
      ca-certificates \
      git \
      gzip \
      libffi \
      nodejs \
      rsync \
      sudo \
      tar \
      unzip \
      util-linux \
      wget \
      zlib-devel

# Install the `Python.h` file for compiling certain libraries.
RUN dnf install python3-devel -y

COPY . .
RUN pip3 install poetry
RUN poetry install --no-root --no-dev

# Install yarn.
# https://linuxize.com/post/how-to-install-yarn-on-centos-8/
RUN dnf install @nodejs -y
RUN curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | tee /etc/yum.repos.d/yarn.repo
RUN rpm --import https://dl.yarnpkg.com/rpm/pubkey.gpg
RUN dnf install yarn -y

# Install app dependencies

RUN yarn install

RUN rm -rf ./static/fonts \
      && cp -rf ./node_modules/uswds/dist/fonts ./static/fonts \
      && yarn build-prod

FROM $IMAGE

### Very low chance of changing
###############################
# Overridable default config
# App directory is provided using `--build-arg APP_DIR=<app-dir>`.
ARG APP_DIR=/opt/atat/atst
# Git SHA is provided using `--build-arg GIT_SHA=<git-sha>`.
ARG GIT_SHA

# Environment variables
ENV APP_DIR "${APP_DIR}"
ENV GIT_SHA "${GIT_SHA}"

# Create application directory
RUN set -x ; \
      mkdir -p ${APP_DIR}

# Set working dir
WORKDIR ${APP_DIR}

# Make `groupadd` command available.
# https://stackoverflow.com/a/44834295
RUN yum install shadow-utils.x86_64 -y

# Create a system group `atat`.
# https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s2-groups-cl-tools
RUN groupadd --system -g 101 atat

# Create a system user `atst` and add them to the `atat` group.
# https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s2-users-cl-tools
RUN useradd --system atst -g atat

# Install postgresql client.
RUN dnf install postgresql-10.6-1.module+el8+2469+5ecd5aae -y

# Install dumb-init.
# dumb-init is a simple process supervisor and init system designed to run as PID 1 inside minimal container environments.
RUN pip3 install dumb-init

# Install the `Python.h` file for compiling certain libraries.
RUN dnf install python3-devel -y

# Install uwsgi and pendulum.
# uwsgi plugins are embedded by default.
# https://uwsgi-docs.readthedocs.io/en/latest/Logging.html#logging-to-files
# Need to build uwsgi with PCRE enabled
RUN yum install pcre pcre-devel -y && pip3 install uwsgi -I && pip3 install pendulum

COPY --from=builder /install/.venv/ ./.venv/
COPY --from=builder /install/alembic/ ./alembic/
COPY --from=builder /install/alembic.ini .
COPY --from=builder /install/app.py .
COPY --from=builder /install/atat/ ./atat/
COPY --from=builder /install/celery_worker.py ./celery_worker.py
COPY --from=builder /install/config/ ./config/
COPY --from=builder /install/policies/ ./policies/
COPY --from=builder /install/templates/ ./templates/
COPY --from=builder /install/translations.yaml .
COPY --from=builder /install/script/ ./script/
COPY --from=builder /install/static/ ./static/
COPY --from=builder /install/fixtures/ ./fixtures
COPY --from=builder /install/uwsgi.ini .

# Use dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]

# Default command is to launch the server
CMD ["uwsgi", "--ini", "uwsgi.ini"]

RUN mkdir /var/run/uwsgi && \
      chown -R atst:atat /var/run/uwsgi && \
      chown -R atst:atat "${APP_DIR}"

RUN update-ca-trust

# Run as the unprivileged APP user
USER atst
