from config.env import env

SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = env.bool("APPEND_SLASH", default=False)
