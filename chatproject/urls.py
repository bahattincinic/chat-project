from django.conf.urls import patterns, include, url
urlpatterns = patterns('',
    # Api
    url(r'^api/', include('api.urls')),
)
