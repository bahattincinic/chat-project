from django.conf.urls import patterns, url, include
from . import api
from auth.api import AccountCreate

account_v1 = patterns('',
    url(r'^$', AccountCreate.as_view(), name='user-account-create'),
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
        url(r'^change-password/$', api.AccountChangePassword.as_view(),
            name='user-change-password'),
        url(r'^$', api.AccountDetail.as_view(),
            name='user-account-detail'),
        )
    ))
)