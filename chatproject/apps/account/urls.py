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
    url(r'^forgot/$', api.ForgotMyPassword.as_view(), name='forgot-password')
)

account_v1 = patterns('',
    url(r'^$', api.AccountCreate.as_view(), name='user-account-create'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/', include(patterns('',
        url(r'^followers/$', api.AccountFollowers.as_view(),
            name='user-account-followers'),
        url(r'^follows/$', api.AccountFollowees.as_view(),
            name='user-account-followees'),
        url(r'^follow/$', api.AccountFollow.as_view(),
            name='user-account-follow'),
        url(r'^report/$', api.AccountReportList.as_view(),
            name='user-reports'),
        url(r'^report/(?P<pk>[0-9]+)/$', api.AccountReportDetail.as_view(),
            name='user-report-detail'),
        url(r'^change_password/$', api.AccountChangePassword.as_view(),
            name='user-change-password'),
        url(r'^$', api.AccountDetail.as_view(),
            name='user-account-detail'),
        )
    ))
)