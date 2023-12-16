# dev.py

from educa.settings.base import *

DEBUG = True

INSTALLED_APPS += ['debug_toolbar']
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# added django_debug_toolbar for docker development, otherwise DDT does not work in docker
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
