# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.permissions import BasePermission
from account.models import User
from utils import SAFE_METHODS


class IsPostOrActiveAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            user = request.user
            if user and user.is_authenticated() and user.is_active:
                return True
            return False
        return True


class IsRequestingUserMatchesUsername(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            username = view.kwargs.get('username')
            user = User.actives.get_or_raise(username=username,
                                             exc=Http404())
            if request.user.id == user.id:
                return True
            return False
        return True
