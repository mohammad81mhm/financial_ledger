from config.env import env

RABBITMQ_USER = env("RABBITMQ_USER", default="guest")
RABBITMQ_PASSWORD = env("RABBITMQ_PASSWORD", default="guest")
RABBITMQ_HOST = env("RABBITMQ_HOST", default="localhost")
RABBITMQ_PORT = env.int("RABBITMQ_PORT", default=5672)
RABBITMQ_BROKER_URL = (
    f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}//"
)
