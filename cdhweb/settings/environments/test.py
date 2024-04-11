import os

from cdhweb.settings import BASE_DIR, DATABASES

# These settings correspond to the service container settings in the
# .github/workflow .yml files.
DATABASES["default"].update(
    {
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "USER": os.getenv("DB_USER"),
        "NAME": os.getenv("DB_NAME"),
        "HOST": "127.0.0.1",
    }
)

# turn off debug so we see 404s when testing
DEBUG = False

# turn off google analytics
INCLUDE_ANALYTICS = False

# required for tests when DEBUG = False
ALLOWED_HOSTS = ["*"]

# configure django-compressor to compress css & javascript
COMPRESS_ENABLED = True

# compress to the sitemedia folder
COMPRESS_ROOT = BASE_DIR / "sitemedia"

# run a full compress before e2e/a11y tests to serve statically
COMPRESS_OFFLINE = True

# override software version to avoid creating visual diffs in display
SW_VERSION = "CI Build"
