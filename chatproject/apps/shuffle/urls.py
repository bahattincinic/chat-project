from django.conf.urls import patterns, include, url
from .api import ShuffleAPIView


shuffle_v1 = patterns('',
    url(r'^$', ShuffleAPIView.as_view()),
)