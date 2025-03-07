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
RUN groupadd -g $GID cap_composer_docker_group || exit 0
RUN useradd --shell /bin/bash -u $UID -g $GID -o -c "" -m cap_composer_docker_user -l || exit 0
ENV DOCKER_USER=cap_composer_docker_user

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

ARG DOCKER_COMPOSE_WAIT_VERSION
ENV DOCKER_COMPOSE_WAIT_VERSION=${DOCKER_COMPOSE_WAIT_VERSION:-2.12.1}
ARG DOCKER_COMPOSE_WAIT_PLATFORM_SUFFIX
ENV DOCKER_COMPOSE_WAIT_PLATFORM_SUFFIX=${DOCKER_COMPOSE_WAIT_PLATFORM_SUFFIX:-}

# Install docker-compose wait
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$DOCKER_COMPOSE_WAIT_VERSION/wait${DOCKER_COMPOSE_WAIT_PLATFORM_SUFFIX} /wait
RUN chown $UID:$GID /wait &&  chmod +x /wait

# Create directories and set correct permissions
RUN mkdir -p /cap_composer/app && chown -R $UID:$GID /cap_composer

USER $UID:$GID

COPY ./cap_composer/requirements/standalone.txt /cap_composer/requirements/
RUN python3 -m venv /cap_composer/venv


ENV PIP_CACHE_DIR=/tmp/cap_composer_pip_cache
# hadolint ignore=SC1091,DL3042
RUN --mount=type=cache,mode=777,target=$PIP_CACHE_DIR,uid=$UID,gid=$GID . /cap_composer/venv/bin/activate && \
     pip3 install  -r /cap_composer/requirements/standalone.txt

COPY --chown=$UID:$GID ./cap_composer /cap_composer/app

# Create a tmp directory for the django to use
RUN mkdir -p /cap_composer/tmp && chown -R $UID:$GID /cap_composer/tmp

WORKDIR /cap_composer/app

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

# install cap_composer as a package
RUN chmod a+x /cap_composer/app/docker/docker-entrypoint.sh && \
    /cap_composer/venv/bin/pip install --no-cache-dir -e /cap_composer/app/


ENTRYPOINT ["/usr/bin/tini", "--", "/bin/bash", "/cap_composer/app/docker/docker-entrypoint.sh"]

# Add the venv to the path. This ensures that the venv is always activated when the container starts.
ENV PATH="/cap_composer/venv/bin:$PATH"

ENV DJANGO_SETTINGS_MODULE='cap_composer.config.settings.production'

CMD ["gunicorn"]