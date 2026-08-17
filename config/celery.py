import os

from celery import Celery

from config.env import BASE_DIR, env

env.read_env(os.path.join(BASE_DIR, ".env"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.local")

celery = Celery("config")
app = celery

celery.config_from_object("django.conf:settings", namespace="CELERY")
celery.autodiscover_tasks()
