# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import BasePermission
from account.models import User
from network.models import Network, NetworkConnection

SAFE_METHODS = ('GET', 'HEAD')


class NetworkDetailPermission(BasePermission):
    def has_permission(self, request, view):
        pk = request.parser_context.get("kwargs").get("pk")
        network = Network.objects.get_or_raise(pk=pk, exc=Http404())
        if request.method in SAFE_METHODS:
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
                    network.check_ownership(request.user):
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

        if request.method in ('POST',) and \
                request.user and \
                request.user.is_authenticated() and \
                User.actives.filter(id=request.user.id):
            return True
        return False


class NetworkAdminPermission(BasePermission):
    def has_permission(self, request, view):
        # everybody can view network mods
        if request.method in SAFE_METHODS:
            return True

        # only admin can assign new mods
        if request.method in ('POST',) and \
                request.user and \
                request.user.is_authenticated():
            pk = request.parser_context.get("kwargs").get("pk")
            network = Network.objects.get_or_raise(pk=pk, exc=Http404())
            if network.check_ownership(user=request.user):
                return True
        return False


class NetworkUserDetailPermission(BasePermission):
    def has_permission(self, request, view):
        # supports get and delete requests
        network_pk = request.parser_context.get("kwargs").get("pk")
        network = Network.objects.get_or_raise(id=network_pk, exc=Http404())

        if request.method in SAFE_METHODS:
            return network.is_public
        elif request.method in ('DELETE',):
            # requesting user must be admin or mod of the network
            # or requesting user id and user_id must be same
            user_pk = request.parser_context.get("kwargs").get("user_pk")
            user = User.actives.get_or_raise(pk=user_pk, exc=Http404())
            # requesting user must be active
            requesting_user = User.actives.get_or_raise(pk=request.user.id,
                                                        exc=Http404())
            # approved connection of this user and network must already exists
            if not NetworkConnection.approved.filter(user=user,
                                                     network=network).exists():
                raise Http404()
            # requesting user must be authenticated
            if not (request.user and request.user.is_authenticated()):
                return False
            # if requesting user has privilege on this network then we allow request
            if network.check_ownership(user=request.user):
                return True
            # or it must be same user leaving the network
            if requesting_user.id == user_pk:
                return True
            # else requesting user cannot remove this network connection
            return False
        # no other operation supported at this moment
        return False

