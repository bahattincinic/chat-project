# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from .models import User
from page.models import Page


class AnonUserProfile(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self):
        return User.actives.all()

    def get_context_data(self, **kwargs):
        context = super(AnonUserProfile, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context

    def get_template_names(self):
        auth_user = self.request.user
        username = self.kwargs.get('username')
        if auth_user.is_authenticated() and auth_user.username == username:
            return 'account/auth_profile.html'
        return 'account/anon_profile.html'
