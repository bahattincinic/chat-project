# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.permissions import BasePermission
from account.models import User
from network.models import Network, NetworkConnection, NetworkAdmin

SAFE_METHODS = ('GET', 'HEAD')


class NetworkDetailPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            network = view.get_object()
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
            network = view.get_object()
            if request.user and \
                    request.user.is_authenticated() and \
                    network.check_ownership(request.user):
                return True
            else:
                return False
        else:
            return False


class IsSafeOrUserActive(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        elif request.user and \
                request.user.is_authenticated() and \
                User.actives.filter(id=request.user.id).exists():
            return True
        return False


class IsSafeOrNoNetworkConnection(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ('POST',):
            network = view.get_network()
            return not NetworkConnection.objects.filter(
                network=network,
                user=request.user).exists()
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
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ('DELETE',):
            # get network connection
            nc = view.get_object()
            # requesting user must be admin or mod of the network
            # or requesting user id and user_id must be same
            user = nc.user
            username = user.username
            # requesting user must be active
            requesting_user = User.actives.get_or_raise(pk=request.user.id, exc=Http404())
            # approved connection of this user and network must already exists
            if not NetworkConnection.approved.filter(user=user,
                                                     network=nc.network).exists():
                raise Http404()
            # if requesting user has privilege on this network then we allow request
            if nc.network.check_ownership(user=request.user):
                return True
            # or it must be same user leaving the network
            if requesting_user.username == username:
                return True
            # else requesting user cannot remove this network connection
            return False
        # no other operation supported at this moment
        return False


class NetworkModsDetailPermission(BasePermission):
    def has_permission(self, request, view):
    # supports get and delete requests
        network_pk = request.parser_context.get("kwargs").get("pk")
        network = Network.objects.get_or_raise(id=network_pk, exc=Http404())
        if request.method in SAFE_METHODS:
            return True
        elif request.method in ('DELETE',):
            # requesting user must be authenticated
            if not request.user and request.user.is_authenticated():
                return False
            # the mod in question
            mod_pk = request.parser_context.get("kwargs").get("mod_pk")
            mod = User.actives.get_or_raise(pk=mod_pk, exc=Http404())
            # mod must really be a moderator of this network
            NetworkAdmin.objects.get_or_raise(user=mod, network=network,
                                              exc=Http404())
            # requesting user must be active
            requesting_user = User.actives.get_or_raise(pk=request.user.id,
                                                        exc=Http404())
            # if requesting user is admin of this network then allow this request
            if network.check_ownership(user=requesting_user, admin=True):
                return True
            # if requesting user is the mod himself
            # then allow this request to proceed
            if mod.id == requesting_user.id:
                return True
            return  False
        return False