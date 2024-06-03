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

# override software version to avoid creating visual diffs in display
SW_VERSION = "CI Build"

ENVIRONMENT = os.getenv('ENVIRONMENT', 'test')
