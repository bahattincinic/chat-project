# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.permissions import BasePermission
from account.models import User
from rest_framework.permissions import SAFE_METHODS


class IsPostOrActiveAuthenticated(BasePermission):
    def has_permission(self, request, view):
        print self.__class__.__name__
        if request.method in SAFE_METHODS:
            user = request.user
            if user and user.is_authenticated() and user.is_active:
                return True
            return False
        print 'ret true'
        return True


class IsPostOrRequestingUserMatchesUsername(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            username = view.kwargs.get('username')
            user = User.actives.get_or_raise(username=username,
                                             exc=Http404())
            if request.user.id == user.id:
                return True
            return False
        return True


class IsRequestingUserDiffThanUrl(BasePermission):
    def has_permission(self, request, view):
        print self.__class__.__name__
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ('POST',) and \
                request.user and \
                request.user.is_authenticated():
            username = view.kwargs.get('username')
            user = User.actives.get_or_raise(username=username, exc=Http404())
            if request.user.id != user.id:
                print 'ret tr 2 tim'
                return True
            return False
        return True
