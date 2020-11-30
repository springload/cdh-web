import os

# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# These settings correspond to the service container settings in the
# .github/workflow .yml files.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.%s' % os.getenv('DJANGO_DB_BACKEND'),
        'USER': os.getenv('DB_NAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'NAME': os.getenv('DB_USER'),
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
