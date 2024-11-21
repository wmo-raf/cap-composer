import os

from .base import *

try:
    from .local import *
except ImportError:
    pass

WAGTAIL_ENABLE_UPDATE_CHECK = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

DEBUG = env('DEBUG', False)

MANIFEST_LOADER = {
    'cache': True,
    # recommended True for production, requires a server restart to pick up new values from the manifest.
}

if os.getenv("EMAIL_SMTP", ""):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_USE_TLS = env.bool("EMAIL_SMTP_USE_TLS", False)
    EMAIL_HOST = env.str('EMAIL_SMTP_HOST', default="localhost")
    EMAIL_PORT = os.getenv("EMAIL_SMTP_PORT", "25")
    EMAIL_HOST_USER = env.str('EMAIL_SMTP_USER', default="")
    EMAIL_HOST_PASSWORD = env.str('EMAIL_SMTP_PASSWORD', default="")

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', cast=None, default=[])

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', cast=None, default=[])
