from django.conf.urls import patterns, include, url
<<<<<<< HEAD
from django.conf import settings
=======
from django.views.generic.base import TemplateView
>>>>>>> sessions_in_sockets
from chat.views import HomePageView
from auth.views import ForgotPassword, NewPasswordView
from account.views import UserProfile

urlpatterns = patterns('',
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^forgot-password/$', ForgotPassword.as_view(),
        name='forgot-my-password'),
    url(r'^new-password/(?P<secret_key>[-_\w]+)/$', NewPasswordView.as_view(),
        name='new-password'),
    url(r'^api/', include('api.urls')),
    url(r'^page/', include('page.urls')),
<<<<<<< HEAD
    url(r'^(?P<username>[-_\w]+)/$', UserProfile.as_view(),
        name='anon-profile')
)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}, name="media"))
=======
    url(r'^node/$', TemplateView.as_view(template_name='chat/node_test.html'), name='node-test'),
    url(r'^internal/', include('internal.urls')),
)
>>>>>>> sessions_in_sockets
