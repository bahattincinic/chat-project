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
    'rest_framework'
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
    'django.middleware.csrf.CsrfViewMiddleware',
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
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # Custom Exception Handler
    'EXCEPTION_HANDLER': 'api.exception.custom_exception_handler',

    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

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

# Api Version
API_VERSION = 'v1'