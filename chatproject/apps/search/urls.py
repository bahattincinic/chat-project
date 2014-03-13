from django.conf.urls import patterns, url
from . import api


search_v1 = patterns('',
    url(r'^user/$', api.UserSearchAPIView.as_view()),
    url(r'^network/$', api.NetworkSearchAPIView.as_view()),
    url(r'^combined/$', api.SearchAPIView.as_view())
)