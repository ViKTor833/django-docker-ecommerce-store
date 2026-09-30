from .base import *
import os

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
