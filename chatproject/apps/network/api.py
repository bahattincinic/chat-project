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
    model = Network


class NetworkConnectionAPIView(ListCreateAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (NetworkConnectionPermission,)
    model = NetworkConnection

    def pre_save(self, obj):
        obj.is_approved = obj.network.is_public


class NetworkUserDetailAPIView(ApiTransactionMixin,
                               RetrieveDestroyAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (NetworkUserDetailPermission,)
    model = NetworkConnection


class NetworkAdminAPIView(ApiTransactionMixin,
                          ListCreateAPIView):
    serializer_class = NetworkAdminAPISerializer
    permission_classes = (NetworkConnectionPermission,)
    model = NetworkAdmin

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        network_pk = kwargs.get('pk')

        try:
            if not (network_pk and Network.objects.filter(pk=network_pk).exists()):
                serializer.errors = {'network': [u'Invalid network']}
                raise OPSException
            network = Network.objects.get(pk=network_pk)
        except OPSException:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.object.network = network
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def pre_save(self, obj):
        assert obj.user, u'Invalid obj'
        assert obj.network, u'Invalid obj'
        obj.status = NetworkAdmin.MODERATOR
        # by default this mod status is not approved
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