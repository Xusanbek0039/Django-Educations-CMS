from educa.settings.base import *

DEBUG = False

ADMINS = (('Admin','admin@admin.com'),)

# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['.educa.com', 'www.educa.com']

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "educa"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "root"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": "5432",
    }
}