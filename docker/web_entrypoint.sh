#!/bin/sh
set -e

echo "--> Applying database migrations"
python manage.py migrate --noinput
python manage.py initial
python manage.py collectstatic --noinput

echo "--> Starting uvicorn"
WORKERS=${WEB_CONCURRENCY:-4}

exec python -m uvicorn config.asgi:application \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${WORKERS}" \
  --proxy-headers \
  --forwarded-allow-ips='*'
