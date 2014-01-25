# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from .models import User


class AnonUserProfile(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'account/anon_profile.html'

    def get_queryset(self):
        return User.actives.all()