from django.conf.urls import patterns, url
from . import api


search_v1 = patterns('',
    url(r'^$', api.UserSearchAPIView.as_view())
)