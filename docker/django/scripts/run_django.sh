#!/bin/bash

set -eux

echo "> Waiting for DB: 'postgres'..."
dockerize -wait tcp://currency_platform_postgres:5432 -timeout 30s

echo "> Migrating models of previous deploy..."
python3 -u manage.py migrate --noinput

echo "> Loading currency data..."
python manage.py loaddata /initial_data/currency_data.json

echo "> Loading provider data..."
python manage.py loaddata /initial_data/provider_data.json

echo "> Starting django (develop mode)"
python3 -u manage.py runserver 0.0.0.0:8000
