import os

# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.

# These settings correspond to the service container settings in the
# .github/workflow .yml files.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cdhweb',
        'USER': 'cdhweb',
        'PASSWORD': 'cdhweb',
        'HOST': '127.0.0.1',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}

# turn off debug so we see 404s when testing
DEBUG = False

# configure django-compressor to compress css & javascript
COMPRESS_ENABLED = True

# compress to the sitemedia folder
COMPRESS_ROOT = os.path.join(BASE_DIR, 'sitemedia')

# run a full compress before e2e/a11y tests to serve statically
COMPRESS_OFFLINE = True
