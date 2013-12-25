# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission

SAFE_METHODS = ('GET', 'HEAD')

class NetworkListPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return False


class NetworkRetrievePermission(BasePermission):
    def has_permission(self, request, view):
        return True



