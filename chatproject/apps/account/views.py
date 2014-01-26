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
        if self.request.user.is_authenticated():
            return 'account/auth_profile.html'
        return 'account/anon_profile.html'
