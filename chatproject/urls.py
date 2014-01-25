from django.conf.urls import patterns, include, url
from django.conf import settings
from chat.views import HomePageView
from auth.views import ForgotPassword, NewPasswordView
from account.views import AnonUserProfile

urlpatterns = patterns('',
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^forgot-password/$', ForgotPassword.as_view(),
        name='forgot-my-password'),
    url(r'^new-password/(?P<secret_key>[-_\w]+)/$', NewPasswordView.as_view(),
        name='new-password'),
    url(r'^api/', include('api.urls')),
    url(r'^page/', include('page.urls')),
    url(r'^(?P<username>[-_\w]+)/$', AnonUserProfile.as_view(),
        name='anon-profile')
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}, name="media"))