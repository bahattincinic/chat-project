# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from . import api
from .validators import uuid_re_url

chat_v1 = patterns('',
   url(r'^$', api.SessionAPIView.as_view(), name='session'),
   url(r'%s/$' % uuid_re_url, api.SessionDetailAPIView.as_view(),
       name='session-detail'),
   url(r'%s/messages/$' % uuid_re_url,
       api.SessionMessageAPIView.as_view(),
       name='session-messages'),
)