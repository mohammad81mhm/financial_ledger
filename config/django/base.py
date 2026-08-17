import logging
import os

from config.env import BASE_DIR, env

env.read_env(os.path.join(BASE_DIR, ".env"))

logging.basicConfig(level=logging.INFO)

from config.settings.core import *  # noqa
from config.settings.apps import *  # noqa
from config.settings.middleware import *  # noqa
from config.settings.templates import *  # noqa
from config.settings.routing import *  # noqa
from config.settings.auth import *  # noqa
from config.settings.i18n import *  # noqa
from config.settings.static import *  # noqa
from config.settings.drf import *  # noqa
from config.settings.cors import *  # noqa
from config.settings.swagger import *  # noqa
from config.settings.database import *  # noqa
from config.settings.redis import *  # noqa
from config.settings.rabbitmq import *  # noqa
from config.settings.celery import *  # noqa
