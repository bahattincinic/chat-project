from configs.base import *

DATABASES["replica"] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3.replica'),
}

LOGGING = {
   'version': 1,
   'disable_existing_loggers': False,
   'filters': {
       'require_debug_false': {
           '()': 'django.utils.log.RequireDebugFalse'
       }
   },
   'handlers': {
       'mail_admins': {
           'level': 'DEBUG',
           'filters': ['require_debug_false'],
           'class': 'django.utils.log.AdminEmailHandler'
       }
   },
   'loggers': {
       'django.request': {
           'handlers': ['mail_admins'],
           'level': 'DEBUG',
           'propagate': True,
       },
   }
}

#ignore the following error when using ipython:
#/django/db/backends/sqlite3/base.py:50: RuntimeWarning:
#SQLite received a naive datetime (2012-11-02 11:20:15.156506)
# while time zone support is active.
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning,
                        module='django.db.backends.sqlite3.base', lineno=58)