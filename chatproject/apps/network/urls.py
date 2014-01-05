# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .api import NetworkAPIView
from .api import NetworkConnectionAPIView
from .api import NetworkDetailAPIView
from network.api import NetworkAdminAPIView, NetworkUserDetailAPIView, NetworkModsDetailAPIView


network_v1 = patterns('',
    url(r'^$', NetworkAPIView.as_view(),
        name='network-lists'),
    url(r'^(?P<pk>[0-9]+)/$', NetworkDetailAPIView.as_view(),
        name='network-detail'),
    url(r'^(?P<pk>[0-9]+)/users/$', NetworkConnectionAPIView.as_view(),
        name='network-users'),
    url(r'^(?P<pk>[0-9]+)/users/(?P<user_pk>[0-9]+)/$',
        NetworkUserDetailAPIView.as_view(),
        name='network-users-detail'),
    url(r'^(?P<pk>[0-9]+)/mods/$', NetworkAdminAPIView.as_view(),
        name='network-mods'),
    url(r'^(?P<pk>[0-9]+)/mods/(?P<mod_pk>[0-9]+)/$',
        NetworkModsDetailAPIView.as_view(),
        name='network-mods-detail'),
)