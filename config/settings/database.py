from config.env import env

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB", default="financial_ledger_db"),
        "USER": env.str("POSTGRES_USER", default="financial_ledger_user"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", default="financial_ledger_password"),
        "HOST": env.str("POSTGRES_HOST", default="localhost"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
    }
}
