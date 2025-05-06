#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset


echo "Running migrations..."
python manage.py migrate

echo "Running collectstatic..."
python manage.py collectstatic --no-input

echo "Starting server"
exec gunicorn --bind :80 --workers 3 somresumido.wsgi:application
