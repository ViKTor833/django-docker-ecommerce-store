from .base import *

DEBUG = True

SECRET_KEY = 'django-insecure-2l&dg&*b%_4-lz(_5_5d2g0=+f#yivz2%(^e16y53qe#+qb0h9'

ALLOWED_HOSTS = []

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
