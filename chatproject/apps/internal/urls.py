from django.conf.urls import patterns, url
from .api import TranslateApiView


urlpatterns = patterns('',
    url(r'^translate/(?P<pk>\d+)/$', TranslateApiView.as_view()),
)