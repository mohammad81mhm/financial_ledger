LOCAL_APPS = [
    "ledger.core.apps.CoreConfig",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "django_celery_results",
    "corsheaders",
    "drf_spectacular",
]

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
