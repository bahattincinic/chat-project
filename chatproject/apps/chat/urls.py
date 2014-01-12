# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from . import api
from .validators import uuid_re_string

chat_v1 = patterns('',
   url(r'^$', api.SessionAPIView.as_view(), name='session'),
   url(uuid_re_string, api.SessionDetailAPIView.as_view(),
       name='session-detail'),
)