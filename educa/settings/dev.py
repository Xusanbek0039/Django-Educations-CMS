from educa.settings.base import *

DEBUG = True

INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# added django_debug_toolbar for docker development, otherwise DDT does not work in docker
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG
}

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "educa"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "root"),
        # "HOST": "host.docker.internal",
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": "5432",
    }
}