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

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn serafin.wsgi:application \
    --name serafin_django \
    --bind 0.0.0.0:8000 \
    --workers 5 \
    --log-level=info \
    --log-file=- \
    --access-logfile=- \
    "$@"
