import os

DEBUG = True

ALLOWED_HOSTS = ["*"]

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
