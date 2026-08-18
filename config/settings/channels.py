"""Django Channels configuration."""

from config.settings.redis import HOST_REDIS, PASSWORD_REDIS, PORT_REDIS

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://:{PASSWORD_REDIS}@{HOST_REDIS}:{PORT_REDIS}/1"],
        },
    },
}
