# -*- coding: utf-8 -*-
from django.views.generic.detail import DetailView
from .models import User
from page.models import Page


class UserProfile(DetailView):
    model = User
    template_name = 'account/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self):
        return User.actives.all()

    def get_user(self, check=False):
        user = self.request.user
        other_user = self.object
        if user.is_authenticated() and user.username == other_user.username:
            return True if check else user
        return False if check else other_user

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        context['type'] = 'me' if self.get_user(check=True) else 'anon'
        context['authenticate'] = self.request.user.is_authenticated()
        return context