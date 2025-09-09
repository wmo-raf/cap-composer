#!/bin/bash
# Bash strict mode: http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

# ======================================================
# ENVIRONMENT VARIABLES USED DIRECTLY BY THIS ENTRYPOINT
# ======================================================

MIGRATE_ON_STARTUP=${MIGRATE_ON_STARTUP:-true}
COLLECT_STATICFILES_ON_STARTUP=${COLLECT_STATICFILES_ON_STARTUP:-true}

CAP_COMPOSER_NUM_OF_GUNICORN_WORKERS=${CAP_COMPOSER_NUM_OF_GUNICORN_WORKERS:-}
CAP_COMPOSER_NUM_OF_CELERY_WORKERS=${CAP_COMPOSER_NUM_OF_CELERY_WORKERS:-}

CAP_COMPOSER_LOG_LEVEL=${CAP_COMPOSER_LOG_LEVEL:-INFO}
CAP_COMPOSER_CELERY_BEAT_DEBUG_LEVEL=${CAP_COMPOSER_CELERY_BEAT_DEBUG_LEVEL:-INFO}

CAP_COMPOSER_PORT="${CAP_COMPOSER_PORT:-8000}"

# get the current version of the app
CAP_COMPOSER_APP_VERSION=$(PYTHONPATH=/capcomposer/app/src/capcomposer python -c "import version; print(version.__version__)")

show_help() {
    echo """
The available CAPComposer related commands and services are shown below:

ADMIN COMMANDS:
manage          : Manage CAPComposer and its database
shell           : Start a Django Python shell
help            : Show this message

SERVICE COMMANDS:
gunicorn            : Start CAPComposer using a prod ready gunicorn server:
                         * Waits for the postgres database to be available first.
                         * Automatically migrates the database on startup.
                         * Binds to 0.0.0.0
gunicorn-wsgi       : Same as gunicorn but runs a wsgi server
celery-worker       : Start the celery worker queue which runs async tasks
celery-beat         : Start the celery beat service used to schedule periodic jobs

DEV COMMANDS:
django-dev      : Start a normal django development server, performs
                  the same checks and setup as the gunicorn command above.

"""
}

show_startup_banner() {
  # Use https://manytools.org/hacker-tools/ascii-banner/ and the font Standard / Wide / Wide to generate
cat <<EOF
=========================================================================================
   ____      _      ____       ____    ___    __  __   ____     ___    ____    _____   ____
  / ___|    / \    |  _ \     / ___|  / _ \  |  \/  | |  _ \   / _ \  / ___|  | ____| |  _ \
 | |       / _ \   | |_) |   | |     | | | | | |\/| | | |_) | | | | | \___ \  |  _|   | |_) |
 | |___   / ___ \  |  __/    | |___  | |_| | | |  | | |  __/  | |_| |  ___) | | |___  |  _ <
  \____| /_/   \_\ |_|        \____|  \___/  |_|  |_| |_|      \___/  |____/  |_____| |_| \_\


Version $CAP_COMPOSER_APP_VERSION

=========================================================================================
EOF
}

run_setup_commands_if_configured() {

        # migrate database
    if [ "$MIGRATE_ON_STARTUP" = "true" ]; then
        echo "python /capcomposer/app/src/capcomposer/manage.py migrate"
        /capcomposer/app/src/capcomposer/manage.py migrate --noinput
    fi

        # collect staticfiles
    if [ "$COLLECT_STATICFILES_ON_STARTUP" = "true" ]; then
        echo "python /capcomposer/app/src/capcomposer/manage.py collectstatic --clear --noinput"
        /capcomposer/app/src/capcomposer/manage.py collectstatic --clear --noinput
    fi
}

start_celery_worker() {

    EXTRA_CELERY_ARGS=()

    if [[ -n "$CAP_COMPOSER_NUM_OF_CELERY_WORKERS" ]]; then
        EXTRA_CELERY_ARGS+=(--concurrency "$CAP_COMPOSER_NUM_OF_CELERY_WORKERS")
    fi
    exec celery -A capcomposer worker "${EXTRA_CELERY_ARGS[@]}" -l INFO "$@"
}

# Lets devs attach to this container running the passed command, press ctrl-c and only
# the command will stop. Additionally they will be able to use bash history to
# re-run the containers command after they have done what they want.
attachable_exec(){
    echo "$@"
    exec bash --init-file <(echo "history -s $*; $*")
}

run_server() {
    run_setup_commands_if_configured

    if [[ "$1" = "wsgi" ]]; then
        STARTUP_ARGS=(capcomposer.config.wsgi:application)
    elif [[ "$1" = "asgi" ]]; then
        STARTUP_ARGS=(-k uvicorn.workers.UvicornWorker capcomposer.config.asgi:application)
    else
        echo -e "\e[31mUnknown run_server argument $1 \e[0m" >&2
        exit 1
    fi

    # Gunicorn args explained in order:
    #
    # 1. See https://docs.gunicorn.org/en/stable/faq.html#blocking-os-fchmod for
    #    why we set worker-tmp-dir to /dev/shm by default.
    # 2. Log to stdout
    # 3. Log requests to stdout
    exec gunicorn --workers="$CAP_COMPOSER_NUM_OF_GUNICORN_WORKERS" \
        --worker-tmp-dir "${TMPDIR:-/dev/shm}" \
        --log-file=- \
        --access-logfile=- \
        --capture-output \
        -b "0.0.0.0:${CAP_COMPOSER_PORT}" \
        --log-level="${CAP_COMPOSER_LOG_LEVEL}" \
        "${STARTUP_ARGS[@]}" \
        "${@:2}"
}

setup_otel_vars(){
  # These key value pairs will be exported on every log/metric/trace by any otel
  # exporters running in subprocesses launched by this script.
  EXTRA_OTEL_RESOURCE_ATTRIBUTES="service.namespace=CAPComposer,"
  EXTRA_OTEL_RESOURCE_ATTRIBUTES+="deployment.environment=${CAP_COMPOSER_DEPLOYMENT_ENV:-unknown}"

  if [[ -n "${OTEL_RESOURCE_ATTRIBUTES:-}" ]]; then
    # If the container has been launched with some extra otel attributes, make sure not
    # to override them with our CAPComposer specific ones.
    OTEL_RESOURCE_ATTRIBUTES="${EXTRA_OTEL_RESOURCE_ATTRIBUTES},${OTEL_RESOURCE_ATTRIBUTES}"
  else
    OTEL_RESOURCE_ATTRIBUTES="$EXTRA_OTEL_RESOURCE_ATTRIBUTES"
  fi
  export OTEL_RESOURCE_ATTRIBUTES
  echo "OTEL_RESOURCE_ATTRIBUTES=$OTEL_RESOURCE_ATTRIBUTES"
}


# ======================================================
# COMMANDS
# ======================================================

if [[ -z "${1:-}" ]]; then
    echo "Must provide arguments to docker-entrypoint.sh"
    show_help
    exit 1
fi

# activate virtualenv
source /capcomposer/venv/bin/activate

show_startup_banner

# wait for required services to be available, using docker-compose-wait
/wait

setup_otel_vars

case "$1" in
django-dev)
    run_setup_commands_if_configured
    echo "Running Development Server on 0.0.0.0:${CAP_COMPOSER_PORT}"
    echo "Press CTRL-p CTRL-q to close this session without stopping the container."
    export OTEL_SERVICE_NAME=capcomposer-dev
    attachable_exec python3 /capcomposer/app/src/capcomposer/manage.py runserver "0.0.0.0:${CAP_COMPOSER_PORT}"
    ;;
django-dev-no-attach)
    run_setup_commands_if_configured
    echo "Running Development Server on 0.0.0.0:${CAP_COMPOSER_PORT}"
    export OTEL_SERVICE_NAME=capcomposer-dev
    python /capcomposer/app/src/capcomposer/manage.py runserver "0.0.0.0:${CAP_COMPOSER_PORT}"
    ;;
gunicorn)
    export OTEL_SERVICE_NAME="capcomposer-asgi"
    run_server asgi "${@:2}"
    ;;
gunicorn-wsgi)
    export OTEL_SERVICE_NAME="capcomposer-wsgi"
    run_server wsgi "${@:2}"
    ;;
manage)
    export OTEL_SERVICE_NAME=capcomposer-manage
    exec python3 /capcomposer/app/src/capcomposer/manage.py "${@:2}"
    ;;
shell)
    export OTEL_SERVICE_NAME=capcomposer-shell
    exec python3 /capcomposer/app/src/capcomposer/manage.py shell
    ;;
celery-worker)
    export OTEL_SERVICE_NAME="capcomposer-celery-worker"
    start_celery_worker -Q celery -n default-worker@%h "${@:2}"
    ;;
celery-worker-healthcheck)
    echo "Running celery worker healthcheck..."
    exec celery -A capcomposer inspect ping -d "default-worker@$HOSTNAME" -t 10 "${@:2}"
    ;;
celery-beat)
    export OTEL_SERVICE_NAME="capcomposer-celery-beat"
    exec celery -A capcomposer beat -l "${CAP_COMPOSER_CELERY_BEAT_DEBUG_LEVEL}" -S django_celery_beat.schedulers:DatabaseScheduler "${@:2}"
    ;;
*)
    echo "Command given was $*"
    show_help
    exit 1
    ;;
esac
