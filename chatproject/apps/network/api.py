# -*- coding: utf-8 -*-
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from core.mixins import ApiTransactionMixin
from network.models import NetworkConnection, NetworkAdmin
from network.permissions import NetworkListCreatePermission, NetworkConnectionPermission
from network.serializers import NetworkAPISerializer, NetworkConnectionAPISerializer
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
        NetworkConnection.objects.create(user=self.request.user,
                                         network=obj,
                                         is_approved=True)
        NetworkAdmin.objects.create(user=self.request.user,
                                    network=obj,
                                    status=NetworkAdmin.ADMIN)
        action.send(self.request.user,
                    verb=NetworkAdmin.verbs.get('assigned'),
                    action_object=obj)


class NetworkDetailAPIView(RetrieveAPIView):
    serializer_class = NetworkDetailAPISerializer
    permission_classes = (NetworkDetailPermission,)
    model = Network


class NetworkConnectionAPIView(ListCreateAPIView):
    serializer_class = NetworkConnectionAPISerializer
    permission_classes = (NetworkConnectionPermission,)
    model = NetworkConnection

    def pre_save(self, obj):
        obj.is_approved = True if obj.network.is_public else False