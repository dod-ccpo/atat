FROM python:3.7.3-alpine3.9 AS builder

ARG CSP
ARG CDN_URL=/static/assets/
ENV TZ UTC

RUN mkdir -p /install/.venv
WORKDIR /install

# Install basic Alpine packages
RUN apk update && \
      apk --no-cache add \
        build-base \
        curl \
        ca-certificates \
        docker \
        git \
        gzip \
        libffi \
        libffi-dev \
        libsass \
        libsass-dev \
        linux-headers \
        nodejs \
        openssh-client \
        openssl \
        openssl-dev \
        pcre-dev \
        postgresql-dev \
        rsync \
        sudo \
        tar \
        util-linux \
        yarn

COPY . .

# Install app dependencies
RUN ./script/write_dotenv && \
      pip install pipenv uwsgi && \
      PIPENV_VENV_IN_PROJECT=1 pipenv sync && \
      yarn install && \
      rm -r ./static/fonts/ &> /dev/null || true && \
      cp -rf ./node_modules/uswds/src/fonts ./static/ && \
      yarn build-prod

## NEW IMAGE
FROM python:3.7.3-alpine3.9

### Very low chance of changing
###############################
# Overridable default config
ARG APP_DIR=/opt/atat/atat

# Environment variables
ENV APP_DIR "${APP_DIR}"

# Create application directory
RUN set -x ; \
  mkdir -p ${APP_DIR}

# Set working dir
WORKDIR ${APP_DIR}

# Add group
RUN addgroup -g 8000 -S "atat" && \
  adduser -u 8010 -D -S -G "atat" "atat"

# Install basic Alpine packages
RUN apk update && \
      apk --no-cache add \
      dumb-init \
      postgresql-client \
      postgresql-dev \
      postgresql-libs \
      uwsgi-logfile \
      uwsgi-python3

COPY --from=builder /install/.venv/ ./.venv/
COPY --from=builder /install/alembic/ ./alembic/
COPY --from=builder /install/alembic.ini .
COPY --from=builder /install/app.py .
COPY --from=builder /install/atat/ ./atat/
COPY --from=builder /install/celery_worker.py ./celery_worker.py
COPY --from=builder /install/config/ ./config/
COPY --from=builder /install/templates/ ./templates/
COPY --from=builder /install/translations.yaml .
COPY --from=builder /install/script/ ./script/
COPY --from=builder /install/static/ ./static/
COPY --from=builder /install/fixtures/ ./fixtures
COPY --from=builder /install/uwsgi.ini .
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to launch the server
CMD ["uwsgi", "--ini", "uwsgi.ini"]

RUN mkdir /var/run/uwsgi && \
      chown -R atat:atat /var/run/uwsgi && \
      chown -R atat:atat "${APP_DIR}"

RUN update-ca-certificates

# Run as the unprivileged APP user
USER atat
