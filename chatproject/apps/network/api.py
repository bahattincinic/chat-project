# -*- coding: utf-8 -*-
from django.http.response import Http404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView
from .models import NetworkConnection, NetworkAdmin
from .permissions import IsSafeOrUserActive, NetworkUserDetailPermission, \
    IsSafeOrNoNetworkConnection, IsSafeOrNetworkUser, IsSafeOrNetworkAdmin, \
    NetworkModsDetailPermission
from network.serializers import NetworkAPISerializer, NetworkConnectionAPISerializer, NetworkAdminAPISerializer
from .permissions import NetworkDetailPermission
from .serializers import NetworkDetailAPISerializer
from .models import Network
from actstream.models import action
from account.models import User


class NetworkAPIView(ListCreateAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = (IsSafeOrUserActive,)
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


class NetworkDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = NetworkDetailAPISerializer
    permission_classes = (NetworkDetailPermission,)
    lookup_field = 'slug'
    model = Network


class NetworkConnectionAPIView(ListCreateAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (IsSafeOrUserActive,
                          IsSafeOrNoNetworkConnection)
    model = Network
    lookup_field = 'slug'

    def get_network(self):
        filtering = {self.lookup_field: self.kwargs.get(self.lookup_field)}
        network = self.model.objects.filter(**filtering).get()
        return network

    def get_queryset(self):
        return NetworkConnection.approved.filter(network=self.get_network())

    def pre_save(self, obj):
        obj.network = self.get_network()
        obj.user = User.actives.get(id=self.request.user.id)
        obj.is_approved = obj.network.is_public


class NetworkConnectionDetailAPIView(RetrieveDestroyAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (IsSafeOrUserActive,
                          NetworkUserDetailPermission)
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


class NetworkModAPIView(ListCreateAPIView):
    serializer_class = NetworkAdminAPISerializer
    permission_classes = (IsSafeOrUserActive,
                          IsSafeOrNetworkUser,
                          IsSafeOrNetworkAdmin)
    model = Network
    lookup_field = 'slug'

    def get_network(self):
        filtering = {self.lookup_field: self.kwargs.get(self.lookup_field)}
        network = self.model.objects.filter(**filtering).get()
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


class NetworkModDetailAPIView(RetrieveDestroyAPIView):
    serializer_class = NetworkAdminAPISerializer
    permission_classes = (IsSafeOrUserActive,
                          NetworkModsDetailPermission,)
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
