FROM registry.atat.codes:443/atat-app-builder:latest

### Very low chance of changing
###############################
ARG APP_USER=atst
ARG APP_GROUP=atat
ARG APP_DIR=/opt/atat/atst
ARG CIBUILD=true

ENV APP_DIR "${APP_DIR}"
ENV FLASK_ENV ci
ENV SKIP_PIPENV true
ENV TORNADO_ENV ci

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Default command is to run all the tests
CMD ["bash", "-c", "${APP_DIR}/script/cibuild"]

# Create application directory
RUN set -x ; \
  mkdir -p ${APP_DIR}

# Set working dir
WORKDIR ${APP_DIR}

# Copy over setup scripts
COPY script/ ./script/

# Add required system packages and app user
RUN set -x ; \
  script/alpine_setup

### Items that will change almost every build
#############################################
# Copy over the rest of the app source
COPY . .

# Install app dependencies
RUN set -x ; \
  script/setup
