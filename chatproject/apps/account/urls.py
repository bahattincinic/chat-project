from django.conf.urls import patterns, url
from .api import ObtainExpiringAuthToken, SessionAuthentication

api_v1 = patterns('',
    url(r'^login/authtoken/$', ObtainExpiringAuthToken.as_view(),
        name='login-token'),
    url(r'^login/session/$', SessionAuthentication.as_view(),
        name='login-session'),
)