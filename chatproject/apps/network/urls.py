# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .api import NetworkAPIView

# Network Api v1
from .api import NetworkDetailAPIView

network_v1 = patterns('',
    url(r'^$', NetworkAPIView.as_view(),
        name='network-lists'),
    url(r'^(?P<pk>[0-9]+)/$', NetworkDetailAPIView.as_view(),
        name='network-detail'),
)