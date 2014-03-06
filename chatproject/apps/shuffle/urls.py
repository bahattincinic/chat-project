# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from .api import ShuffleAPIView, NetworkShuffleApiView


shuffle_v1 = patterns('',
    url(r'^all/$', ShuffleAPIView.as_view()),
    url(r'^network/(?P<slug>[A-Za-z0-9-_]+)/$', NetworkShuffleApiView.as_view()),
)

