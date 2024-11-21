# syntax = docker/dockerfile:1.5

# use osgeo gdal ubuntu small 3.10.0 image.
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.10.0

ARG UID
ENV UID=${UID:-9999}
ARG GID
ENV GID=${GID:-9999}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# We might be running as a user which already exists in this image. In that situation
# Everything is OK and we should just continue on.
RUN groupadd -g $GID alertwise_docker_group || exit 0
RUN useradd --shell /bin/bash -u $UID -g $GID -o -c "" -m alertwise_docker_user -l || exit 0
ENV DOCKER_USER=alertwise_docker_user

ENV POSTGRES_VERSION=15


# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    lsb-release \
    ca-certificates \
    gnupg2 \
    curl \
    tini \
    libpq-dev \
    libgeos-dev \
    imagemagick \
    libmagic1 \
    libcairo2-dev \
    libpangocairo-1.0-0 \
    libffi-dev \
    python3-pip \
    python3-dev \
    python3-venv \
    poppler-utils \
    git \
    gosu \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && curl --silent https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    postgresql-client-$POSTGRES_VERSION \
    && apt-get autoclean \
    && apt-get clean \
    && apt-get autoremove \
    && rm -rf /var/lib/apt/lists/*

ENV DOCKER_COMPOSE_WAIT_VERSION=2.12.1

# Install docker-compose wait
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$DOCKER_COMPOSE_WAIT_VERSION/wait /wait
RUN chmod +x /wait

# Create directories and set correct permissions
RUN mkdir -p /alertwise/app && chown -R $UID:$GID /alertwise

USER $UID:$GID

COPY ./alertwise/requirements/base.txt /alertwise/requirements/
RUN python3 -m venv /alertwise/venv


ENV PIP_CACHE_DIR=/tmp/alertwise_pip_cache
# hadolint ignore=SC1091,DL3042
RUN --mount=type=cache,mode=777,target=$PIP_CACHE_DIR,uid=$UID,gid=$GID . /alertwise/venv/bin/activate && \
     pip3 install  -r /alertwise/requirements/base.txt

COPY --chown=$UID:$GID ./alertwise /alertwise/app

# Create a tmp directory for the django to use
RUN mkdir -p /alertwise/tmp && chown -R $UID:$GID /alertwise/tmp

WORKDIR /alertwise/app

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

# install alertwise as a package
RUN chmod a+x /alertwise/app/docker/docker-entrypoint.sh && \
    /alertwise/venv/bin/pip install --no-cache-dir -e /alertwise/app/


ENTRYPOINT ["/usr/bin/tini", "--", "/bin/bash", "/alertwise/app/docker/docker-entrypoint.sh"]

# Add the venv to the path. This ensures that the venv is always activated when the container starts.
ENV PATH="/alertwise/venv/bin:$PATH"

ENV DJANGO_SETTINGS_MODULE='alertwise.config.settings.production'

CMD ["gunicorn"]