from django.conf.urls import patterns, url
from .api import TranslateApiView


urlpatterns = patterns('',
    url(r'^$', 'chatproject.apps.internal.views.close_session'),
    url(r'^translate/(?P<pk>\d+)/$', TranslateApiView.as_view(), name='translate-id-username'),
)