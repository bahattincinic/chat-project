# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from . import api
from .validators import uuid_re_url

chat_v1 = patterns('',
    url(r'^$', api.SessionAPIView.as_view(), name='session'),
    # session url group
    url(r'%s/' % uuid_re_url, include(patterns('',
        url(r'^$', api.SessionDetailAPIView.as_view(),
            name='session-detail'),
        url(r'^messages/$', api.SessionMessageAPIView.as_view(),
            name='session-messages'),
    )))
)