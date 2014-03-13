# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework import generics
from .models import NetworkConnection, NetworkAdmin, Network
from actstream.models import action
from account.models import User
from . import permissions
from . import serializers


class NetworkAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.NetworkAPISerializer
    permission_classes = (permissions.IsSafeOrUserActive,)
    model = Network

    def pre_save(self, obj):
        obj.created_by = self.request.user

    def post_save(self, obj, created=False):
        if not created:
            return

        # now create a new NetworkAdmin and NetworkConnection
        connection = NetworkConnection.objects.create(user=self.request.user,
                                                      network=obj,
                                                      is_approved=True)
        NetworkAdmin.objects.create(user=self.request.user,
                                    network=obj,
                                    status=NetworkAdmin.ADMIN,
                                    connection=connection)
        action.send(self.request.user,
                    verb=NetworkAdmin.verbs.get('assigned'),
                    action_object=obj)


class NetworkDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.NetworkDetailAPISerializer
    permission_classes = (permissions.NetworkDetailPermission,)
    lookup_field = 'slug'
    model = Network

    def post_delete(self, obj):
        print 'network post_delete sea view'


class NetworkConnectionAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.NetworkConnectionAPISerializer
    permission_classes = (permissions.IsSafeOrUserActive,
                          permissions.IsSafeOrNoNetworkConnection)
    model = Network
    lookup_field = 'slug'

    def get_network(self):
        filtering = {self.lookup_field: self.kwargs.get(self.lookup_field)}
        network = self.model.objects.get_or_raise(exc=Http404(), **filtering)
        return network

    def get_queryset(self):
        return NetworkConnection.approved.filter(network=self.get_network())

    def pre_save(self, obj):
        obj.network = self.get_network()
        obj.user = User.actives.get(id=self.request.user.id)
        obj.is_approved = obj.network.is_public


class NetworkConnectionDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.NetworkConnectionAPISerializer
    permission_classes = (permissions.IsSafeOrUserActive,
                          permissions.NetworkUserDetailPermission)
    model = Network
    lookup_field = 'slug'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        slug = self.kwargs.get('slug')
        user = User.actives.get_or_raise(username=username, exc=Http404())
        network = Network.objects.get_or_raise(slug=slug, exc=Http404())
        nc = NetworkConnection.approved.get_or_raise(
            user=user,
            network=network,
            exc=Http404())
        return nc


class NetworkModAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.NetworkAdminAPISerializer
    permission_classes = (permissions.IsSafeOrUserActive,
                          permissions.IsSafeOrNetworkUser,
                          permissions.IsSafeOrNetworkAdmin)
    model = Network
    lookup_field = 'slug'

    def get_network(self):
        filtering = {self.lookup_field: self.kwargs.get(self.lookup_field)}
        network = self.model.objects.get_or_raise(exc=Http404(), **filtering)
        return network

    def get_queryset(self):
        return NetworkAdmin.objects.filter(network=self.get_network())

    def pre_save(self, obj):
        network = self.get_network()
        connection = NetworkConnection.approved.get_or_raise(user=obj.user,
                                                             exc=Http404())
        obj.network = network
        obj.status = NetworkAdmin.MODERATOR
        obj.connection = connection


class NetworkModDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.NetworkAdminAPISerializer
    permission_classes = (permissions.IsSafeOrUserActive,
                          permissions.NetworkModsDetailPermission,)
    model = Network
    lookup_field = 'slug'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        slug = self.kwargs.get('slug')
        user = User.actives.get_or_raise(username=username, exc=Http404())
        network = Network.objects.get_or_raise(slug=slug, exc=Http404())
        na = NetworkAdmin.objects.get_or_raise(
            user=user,
            network=network,
            status=NetworkAdmin.MODERATOR,
            exc=Http404())
        return na
