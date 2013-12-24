# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .api import NetworkAPIView

# Network Api v1
network_v1 = patterns('',
    url(r'^list/$', NetworkAPIView.as_view(), name='network-lists'),

    # url(r'^login/session/$', NetworkAPIView.as_view(),
    #     name='login-session'),
)
