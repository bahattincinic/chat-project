from django.conf.urls import patterns, url
from .api import TranslateApiView
from internal.api import OnlineUsersAPIView


urlpatterns = patterns('',
    url(r'^translate/(?P<pk>\d+)/$', TranslateApiView.as_view()),
    url(r'^active/$', OnlineUsersAPIView.as_view()),
)
