import os

# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# These settings correspond to the service container settings in the
# .github/workflow .yml files.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': os.getenv('POSTGRES_USER'),
        'NAME': os.getenv('POSTGRES_DB'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '',
    },
}

# turn off debug so we see 404s when testing
DEBUG = False

# required for tests when DEBUG = False
ALLOWED_HOSTS = ['*']

# configure django-compressor to compress css & javascript
COMPRESS_ENABLED = True

# compress to the sitemedia folder
COMPRESS_ROOT = os.path.join(BASE_DIR, 'sitemedia')

# run a full compress before e2e/a11y tests to serve statically
COMPRESS_OFFLINE = True
