#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput

if [[ "${DJANGO_SUPERUSER_RESET_PASSWORD:-}" == "true" ]]; then
    python manage.py bootstrap_admin --reset-password
else
    python manage.py bootstrap_admin
fi

exec gunicorn holbos_attendance.holbos_project.wsgi:application --bind "0.0.0.0:${PORT}" --workers 2 --timeout 120
