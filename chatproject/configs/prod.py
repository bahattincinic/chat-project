from configs.base import *

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'sentry@burakalkan.com'
EMAIL_HOST_PASSWORD = 'AlphaAlphaPicard'
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = 'sentry@burakalkan.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'chatproject',
        'USER': 'chat',
        'PORT': '5432',
        'HOST': 'localhost',
        'PASSWORD': 'oohs8:wising'
    }
}

DEBUG = False
