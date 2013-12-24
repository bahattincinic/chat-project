# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class PublicNetworkPermission(BasePermission):
    def has_permission(self, request, view):
        print "public permission is here"
        return True


class PrivateNetworkPermission(BasePermission):
    def has_permission(self, request, view):
        print "priv network permission "
        return True


