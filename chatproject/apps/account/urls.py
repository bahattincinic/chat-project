from django.conf.urls import patterns, url
from . import api


auth_v1 = patterns('',
    url(r'^login/authtoken/$', api.ObtainExpiringAuthToken.as_view(),
        name='login-token'),
    url(r'^login/session/$', api.SessionAuthentication.as_view(),
        name='login-session'),
    url(r'^logout/session/$', api.SessionLogout.as_view(),
        name='logout-session'),
    url(r'^logout/authtoken/$', api.TokenLogout.as_view(),
        name='logout-token'),
    url(r'^forgot/$', api.ForgotMyPassword.as_view(),
        name='forgot-password')
)

account_v1 = patterns('',
    url(r'^$', api.AccountCreate.as_view(), name='user-account-create'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/followers/$',
        api.AccountFollowers.as_view(), name='user-account-followers'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/follows/$',
        api.AccountFollowings.as_view(), name='user-account-followings'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/follow/$',
        api.AccountFollow.as_view(), name='user-account-follow'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/$', api.AccountDetail.as_view(),
        name='user-account-detail'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/report/$',
        api.AccountReportList.as_view(), name='user-reports'),
    url(r'^(?P<username>[A-Za-z0-9-_]+)/report/(?P<pk>[0-9]+)/$',
        api.AccountReportDetail.as_view(), name='user-report-detail'),
)