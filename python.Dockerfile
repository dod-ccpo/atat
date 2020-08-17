# Image source is provided using `--build-arg IMAGE=<some-image>`.
# https://docs.docker.com/engine/reference/commandline/build/#options
ARG IMAGE

FROM $IMAGE

# Removes the specified packages from the system along with any
# packages depending on the packages being removed.
# https://man7.org/linux/man-pages/man8/yum.8.html
RUN yum remove python3

# Removes all “leaf” packages from the system that were originally
# installed as dependencies of user-installed packages, but which
# are no longer required by any such package.
# https://man7.org/linux/man-pages/man8/yum.8.html
RUN yum autoremove python3

# Update package repository information.
# http://man7.org/linux/man-pages/man8/yum.8.html
RUN yum updateinfo

# Upgrade all packages with their latest security updates.
# http://man7.org/linux/man-pages/man8/yum.8.html
RUN yum upgrade --security

# Necessary for building python.
RUN yum install -y gcc libffi-devel make wget zlib-devel

# Causes python to be built with SSL capabilitiy, allowing pip to function.
RUN yum install -y openssl-devel

# Register this machine with a RedHat subscription.
# Enables us to add the CodeReady repository.
RUN subscription-manager remove --all
RUN subscription-manager clean
RUN subscription-manager register --username $REDHAT_USERNAME --password $REDHAT_PASSWORD
RUN subscription-manager refresh
RUN subscription-manager attach --auto

# Enable the CodeReady repository.
# Allows us to install the xmlsec1-devel package.
# https://access.redhat.com/articles/4348511#enable
RUN subscription-manager repos --enable codeready-builder-for-rhel-8-x86_64-rpms

# Install dependencies of python3-saml.
RUN yum install -y libxml2-devel xmlsec1 xmlsec1-openssl libtool-ltdl-devel xmlsec1-devel

# Enable python3 to be built with sqlite extensions.
RUN yum install -y sqlite sqlite-devel 

# Install python!
# https://github.com/python/cpython#build-instructions
RUN cd /usr/src \
    && wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz \
    && tar xzf Python-3.7.3.tgz \
    && cd Python-3.7.3 \
    && ./configure --enable-loadable-sqlite-extensions --enable-optimizations \
    && make install \
    && rm /usr/src/Python-3.7.3.tgz
