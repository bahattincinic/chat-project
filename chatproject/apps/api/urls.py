# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from account.urls import account_v1
from auth.urls import auth_v1
from network.urls import network_v1
from page.urls import page_v1
from search.urls import search_v1
from django.conf import settings


# Api V1
v1_routers = patterns('',
    url(r'^account/', include(account_v1)),
    url(r'^auth/', include(auth_v1)),
    url(r'^page/', include(page_v1)),
    url(r'^network/', include(network_v1)),
    url(r'^search/', include(search_v1))
)

v1_routers = format_suffix_patterns(v1_routers,
                                    allowed=settings.API_ALLOWED_FORMATS)

urlpatterns = patterns('',
    url(r'^%s/' % settings.API_VERSION, include(v1_routers)),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')))

