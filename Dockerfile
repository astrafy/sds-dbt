FROM python:3.11.9-slim-bookworm

#Installation of dbt
RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends
# Env vars
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8
# Update python

RUN pip install poetry
WORKDIR /app

# Copy your project files into the container
COPY ./pyproject.toml /app/pyproject.toml
WORKDIR /app/
RUN poetry config virtualenvs.create false --local
# Install dependencies using Poetry
RUN poetry install

ARG PACKAGE=*
COPY dbt /app
COPY ./docker_install_dbt_package.sh /app/
COPY ./profiles.yml /app/profiles.yml
RUN chmod u+x /app/docker_install_dbt_package.sh
RUN /app/docker_install_dbt_package.sh $PACKAGE

WORKDIR /app/$PACKAGE
