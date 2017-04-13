#!/bin/bash
python manage.py run_huey &
python manage.py runserver 0.0.0.0:8000
