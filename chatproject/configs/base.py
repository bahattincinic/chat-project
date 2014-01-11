"""
Django settings for chatproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import djcelery

djcelery.setup_loader()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APPS = os.path.join(BASE_DIR, 'apps')
# CONFIG = os.path.join(BASE_DIR, 'configs')
sys.path.insert(1, APPS)
sys.path.insert(2, BASE_DIR)
# sys.path.insert(3, CONFIG)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xv-#91!%mv!(m0yba%t0^1t683mvwj_c!5d1z--^8!2x5z(6ss'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# TEMPLATE CONFIGURATION
# See:
# https://docs.djangoproject.com/en/dev/ref/
# settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates')
)
# END TEMPLATE CONFIGURATION

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = 'account.User'


# APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'rest_framework',
    'djcelery'
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'actstream',
    'account',
    'api',
    'chat',
    'network'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'chatproject.urls'

WSGI_APPLICATION = 'chatproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Rest Framework Config http://django-rest-framework.org/#installation
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'auth.authentication.ExpiringTokenAuthentication'
    ),
    # Custom Exception Handler
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',

    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
    ),
    # Pagination settings
    'PAGINATE_BY': 5, # TODO: burasi arttirilmali daha sonra
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100,
}

CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

# Celery Config
BROKER_URL = "amqp://guest:guest@localhost:5672//"

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DEFAULT_FROM_EMAIL = "system@chatproject.com"

EMAIL_BACKEND = 'core.mail.backends.CeleryEmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Devices
DESKTOP = 'desktop'
MOBILE = 'mobile'
IOS = 'ios'
ANDROID = 'android'
DEVICE_CHOCIES = ((DESKTOP, 'Desktop'), (IOS, 'ios'),
                  (ANDROID, 'Android'), (MOBILE, 'Mobile'))

AUTH_SESSION = 'authsession'
TOKEN_SESSION = 'tokensession'
AUTH_TYPES = ((AUTH_SESSION, 'Auth Session'), (TOKEN_SESSION, 'Token Session'))

# Api
API_VERSION = 'v1'
API_ALLOWED_FORMATS = ['json']
# 15 days
API_TOKEN_TTL = 15
