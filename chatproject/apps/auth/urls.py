from django.conf.urls import patterns, url, include
from . import api

auth_v1 = patterns('',
    url(r'^login/', include(patterns('',
        url(r'^authtoken/$', api.ObtainExpiringAuthToken.as_view(),
            name='login-token'),
        url(r'^session/$', api.SessionAuthentication.as_view(),
            name='login-session'),
        )
    )),
    url(r'^logout/', include(patterns('',
        url(r'^session/$', api.SessionLogout.as_view(), name='logout-session'),
        url(r'^authtoken/$', api.TokenLogout.as_view(), name='logout-token'),
        )
    )),
    url(r'^forgot/', include(patterns('',
        url(r'^password/$', api.ForgotPassword.as_view(),
            name='forgot-password'),
        url(r'^username/$', api.ForgotUsername.as_view(),
            name='forgot-username'),
        url(r'^new-password/$', api.ForgotNewPassword.as_view(),
            name='forgot-new-password'),
        )
    ))
)