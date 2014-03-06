from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from chat.views import HomePageView
from auth.views import ForgotPassword, NewPasswordView

urlpatterns = patterns('',
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^forgot-password/$', ForgotPassword.as_view(),
        name='forgot-my-password'),
    url(r'^new-password/(?P<secret_key>[-_\w]+)/$', NewPasswordView.as_view(),
        name='new-password'),
    url(r'^api/', include('api.urls')),
    url(r'^page/', include('page.urls')),
    url(r'^node/$', TemplateView.as_view(template_name='chat/node_test.html')),
    url(r'^internal/', include('internal.urls')),
)