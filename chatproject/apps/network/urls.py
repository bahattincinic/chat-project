# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .api import NetworkAPIView
from .api import NetworkConnectionAPIView
from .api import NetworkDetailAPIView
from network.api import NetworkModAPIView, NetworkConnectionDetailAPIView, NetworkModDetailAPIView


network_v1 = patterns('',
    url(r'^$', NetworkAPIView.as_view(),
        name='network-lists'),
    # retrieve, update, destroy a network
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/$', NetworkDetailAPIView.as_view(),
        name='network-detail'),
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/users/$', NetworkConnectionAPIView.as_view(),
        name='network-users'),
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/users/(?P<username>[A-Za-z0-9-_]+)/$',
        NetworkConnectionDetailAPIView.as_view(),
        name='network-users-detail'),
    # list and create mod
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/mods/$', NetworkModAPIView.as_view(),
        name='network-mods'),
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/mods/(?P<username>[A-Za-z0-9-_]+)/$',
        NetworkModDetailAPIView.as_view(),
        name='network-mods-detail'),
)