from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'chatproject.apps.internal.views.close_session'),
    url(r'^translate/(?P<userid>\d+)/$',
        'chatproject.apps.internal.views.translate_user_id',
        name='translate-id-username'),
)