from django.conf.urls import patterns, url
from .api import PageDetailAPIView, PageListAPIView
from .views import PageDetailView

page_v1 = patterns('',
    url(r'^$', PageListAPIView.as_view(),
        name='page-list'),
    url(r'^(?P<slug>[A-Za-z0-9-_]+)/$', PageDetailAPIView.as_view(),
        name='page-detail'),
)

urlpatterns = patterns('',
    url(r'^(?P<slug>[-_\w]+)/$', PageDetailView.as_view(), name='page-detail')
)