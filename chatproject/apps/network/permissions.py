# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.permissions import BasePermission
from account.models import User
from network.models import Network, NetworkConnection

SAFE_METHODS = ('GET', 'HEAD')


class NetworkDetailPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            pk = request.parser_context.get("kwargs").get("pk")
            network = Network.objects.get_or_raise(pk=pk, exc=Http404())
            if network.is_public:
                return True
            else:
                # network is private check if
                # user is part of this network
                if request.user and \
                        request.user.is_authenticated() and \
                        NetworkConnection.check_membership(request.user, network):
                    return True
                return False
        elif request.method in ('PUT', 'PATCH', 'DELETE'):
            if request.user and \
                    request.user.is_authenticated() and \
                    Network.check_ownership(request.user):
                return True
            else:
                return False
        else:
            return False


class NetworkListCreatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.method == 'POST' and \
                request.user and \
                request.user.is_authenticated() and \
                User.actives.filter(id=request.user.id).exists():
            # TODO: maybe check for throttling as well
            return True
        return False


class NetworkConnectionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if request.mothod in ('POST',) and \
                request.user and \
                request.user.is_authenticated() and \
                User.actives.filter(id=request.user.id):
            return True
        return False