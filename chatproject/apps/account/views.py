# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from .models import User


class AnonUserProfile(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self):
        return User.actives.all()

    def get_template_names(self):
        auth_user = self.request.user
        username = self.kwargs.get('username')
        if auth_user.is_authenticated() and auth_user.username == username:
            return 'account/auth_profile.html'
        return 'account/anon_profile.html'
