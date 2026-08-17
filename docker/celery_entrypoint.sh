#!/bin/sh
set -e

echo "--> Starting Celery worker"
exec celery -A config worker -l info --concurrency="${CELERY_CONCURRENCY:-4}"
