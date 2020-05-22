# Image source is provided using `--build-arg IMAGE=<some-image>`.
# https://docs.docker.com/engine/reference/commandline/build/#options
ARG IMAGE

FROM $IMAGE

RUN set -x \
    # Create a system group `nginx`.
    # https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s2-groups-cl-tools
    && groupadd --system -g 101 nginx \
    # Create a system user `nginx` with a non-existent home directory and add them to the `nginx` group.
    # https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/deployment_guide/s2-users-cl-tools
    && useradd --system -d /dev/null nginx -g nginx \
    # Update the `nginx` user to not have a login shell.
    # https://access.redhat.com/articles/2072
    && usermod -s /sbin/nologin nginx \
    # Update package repository information.
    # http://man7.org/linux/man-pages/man8/yum.8.html
    && yum updateinfo \
    # Upgrade all packages with their latest security updates.
    # http://man7.org/linux/man-pages/man8/yum.8.html
    && yum upgrade --security \ 
    # Install nginx!
    # https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/#prebuilt_redhat
    && yum install nginx -y

# Replace the default nginx settings to bind to an unprivileged port.
RUN sed -i "s|80 default_server|8080 default_server|g" /etc/nginx/nginx.conf

# Forward request and error logs to Docker log collector.
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 8080

STOPSIGNAL SIGTERM

# Give the unprivilieged nginx user ownership of its pid file.
RUN touch /run/nginx.pid
RUN chown nginx /run/nginx.pid

# Run as the unprivileged nginx user.
# https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
USER nginx

CMD ["nginx", "-g", "daemon off;"]
