# -*- coding: utf-8 -*-
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from core.exceptions import OPSException
from core.mixins import ApiTransactionMixin
from network.models import NetworkConnection, NetworkAdmin
from network.permissions import NetworkListCreatePermission, NetworkConnectionPermission, NetworkUserDetailPermission
from network.serializers import NetworkAPISerializer, NetworkConnectionAPISerializer, NetworkAdminAPISerializer
from .permissions import NetworkDetailPermission
from .serializers import NetworkDetailAPISerializer
from .models import Network
from actstream.models import action


class NetworkAPIView(ApiTransactionMixin, ListCreateAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = (NetworkListCreatePermission,)
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


class NetworkDetailAPIView(ApiTransactionMixin,
                           RetrieveUpdateDestroyAPIView):
    serializer_class = NetworkDetailAPISerializer
    permission_classes = (NetworkDetailPermission,)
    lookup_field = 'slug'
    model = Network


class NetworkConnectionAPIView(ListCreateAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (NetworkConnectionPermission,)
    model = NetworkConnection
    lookup_field = 'user__username'

    def pre_save(self, obj):
        obj.is_approved = obj.network.is_public


class NetworkUserDetailAPIView(ApiTransactionMixin,
                               RetrieveDestroyAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (NetworkUserDetailPermission,)
    model = NetworkConnection
    lookup_field = 'slug'


class NetworkAdminAPIView(ApiTransactionMixin,
                          ListCreateAPIView):
    serializer_class = NetworkAdminAPISerializer
    permission_classes = (NetworkConnectionPermission,)
    model = NetworkAdmin

    def pre_save(self, obj):
        assert obj.user, u'Invalid obj'
        # set network of this NetworkAdmin obj
        network_pk = self.kwargs.get('pk')
        network = Network.objects.get(pk=network_pk)
        obj.network = network
        obj.status = NetworkAdmin.MODERATOR
        # by default this mod status is not approved
        # since it is mod request
        obj.is_approved = False
        conn = NetworkConnection.objects.create(user=obj.user,
                                                network=obj.network,
                                                is_approved=False)
        conn.save()
        obj.connection = conn


class NetworkModsDetailAPIView(ApiTransactionMixin,
                               RetrieveDestroyAPIView):
    serializer_class = NetworkAdminAPISerializer
    permission_classes = (NetworkUserDetailPermission,)
    model = NetworkAdmin