# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework.generics import RetrieveAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny
from network.models import NetworkConnection, NetworkAdmin
from network.permissions import NetworkListCreatePermission
from network.serializers import NetworkListAPISerializer
from .permissions import NetworkDetailPermission
from .serializers import NetworkAPISerializer
from .models import Network


class NetworkAPIView(ListCreateAPIView):
    serializer_class = NetworkListAPISerializer
    permission_classes = (NetworkListCreatePermission,)
    model = Network

    def pre_save(self, obj):
        obj.created_by = self.request.user

    def post_save(self, obj, created=False):
        if not created:
            return

        with transaction.atomic():
            # now create a new NetworkAdmin and NetworkConnection
            NetworkConnection.objects.create(user=self.request.user,
                                             network=obj,
                                             is_approved=True)
            NetworkAdmin.objects.create(user=self.request.user,
                                        network=obj,
                                        status=NetworkAdmin.ADMIN)


class NetworkDetailAPIView(RetrieveAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = (NetworkDetailPermission,)
    model = Network
