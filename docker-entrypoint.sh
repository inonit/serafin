#!/bin/bash
if [ "$1" = "--migrate" ]; then
    python manage.py migrate                  # Apply database migrations
    exit
elif [ "$1" = "--worker" ]; then
    shift
    exec python manage.py "$@"
    exit
fi

python manage.py collectstatic --noinput # TODO: Move to docker build?

supervisord -c /etc/supervisor/supervisor.conf
