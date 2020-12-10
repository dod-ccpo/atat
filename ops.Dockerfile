ARG IMAGE=cloudzeroopsregistry.azurecr.io/rhel-py:latest

FROM $IMAGE

COPY ./azure-cli.repo /etc/yum.repos.d/azure-cli.repo

RUN yum -y update && \
  rpm --import https://packages.microsoft.com/keys/microsoft.asc &&  \
  yum install -y azure-cli bzip2-devel gettext git jq openssl-devel postgresql-devel unzip && \
  curl https://releases.hashicorp.com/terraform/0.13.5/terraform_0.13.5_linux_amd64.zip -o tf.zip && \
  unzip tf.zip && \
  sudo mv terraform /usr/local/bin && \
  ln -s /usr/bin/python /usr/bin/python3.7 && \
  cd /tmp && \
  curl --retry 10 -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
  chmod +x /tmp/kubectl && \
  sudo mv /tmp/kubectl /usr/bin/kubectl && \
  curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 && \
  chmod 700 get_helm.sh && \
  ./get_helm.sh
#  && \
# pip3 install --upgrade pip

COPY ./ops/requirements.txt /src/ops/requirements.txt

RUN pip3 install -r /src/ops/requirements.txt && \
  pip3 install ansible==2.9 \
  openshift \
  pyhcl && \
  pip3 install ansible[azure] azure-storage-common azure-common azure-storage-blob azure-storage-nspkg pydantic onelogin python3-saml


WORKDIR /src

COPY . /src

WORKDIR /src/ops/phase2

ENTRYPOINT "/bin/bash"
