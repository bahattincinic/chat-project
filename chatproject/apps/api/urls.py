# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings
from rest_framework.urlpatterns import format_suffix_patterns
from account.urls import account_v1
from network.urls import network_v1

# Api V1
v1_routers = patterns('',
    url(r'^account/', include(account_v1)),
    url(r'^network/', include(network_v1)),
)

v1_routers = format_suffix_patterns(v1_routers,
                                    allowed=settings.API_ALLOWED_FORMATS)

urlpatterns = patterns('',
    url(r'^%s/' % settings.API_VERSION, include(v1_routers)),
)