from config.env import env

HOST_REDIS = env("HOST_REDIS", default="localhost")
PORT_REDIS = env.int("PORT_REDIS", default=6379)
PASSWORD_REDIS = env("PASSWORD_REDIS", default="")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{PASSWORD_REDIS}@{HOST_REDIS}:{PORT_REDIS}/0",
    }
}
