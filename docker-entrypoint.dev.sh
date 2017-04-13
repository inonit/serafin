#!/bin/bash
python manage.py migrate --noinput
python manage.py migrate --noinput --database vault

python manage.py run_huey &
python manage.py runserver 0.0.0.0:8000
