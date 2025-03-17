FROM python:3.11.9-slim-bookworm

#Installation of dbt
RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libpq-dev \
  && apt-get clean \
  && rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/*
# Env vars
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
# Update python
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir
COPY ./docker_requirement.txt /opt/dbt/requirements.txt
RUN pip install -r /opt/dbt/requirements.txt



ARG PACKAGE=*

COPY ./docker_install_dbt_package.sh /app/
COPY ./profiles.yml /app/profiles.yml
RUN chmod u+x /app/docker_install_dbt_package.sh

COPY dbt /app

RUN /app/docker_install_dbt_package.sh $PACKAGE

WORKDIR /app/$PACKAGE