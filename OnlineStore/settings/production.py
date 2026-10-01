from .base import *
import os

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

X_FRAME_OPTIONS = 'DENY'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
