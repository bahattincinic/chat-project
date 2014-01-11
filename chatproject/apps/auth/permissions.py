# -*- coding: utf-8 -*-
from rest_framework import permissions


class UserCreatePermission(permissions.BasePermission):
    """
    User Register Permission
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.is_anonymous()
        else:
            return False