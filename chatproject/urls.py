from django.conf.urls import patterns, include, url
from chat.views import HomePageView

urlpatterns = patterns('',
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^api/', include('api.urls')),
    url(r'^page/', include('page.urls')),
)