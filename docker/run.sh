#!/bin/bash

cd /app/server
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver 0.0.0.0:8000