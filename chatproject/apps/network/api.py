# -*- coding: utf-8 -*-
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from network.serializers import NetworkListAPISerializer
from .permissions import NetworkDetailPermission
from .serializers import NetworkAPISerializer
from .models import Network
from account.models import User


class NetworkAPIView(ListAPIView):
    serializer_class = NetworkListAPISerializer
    permission_classes = (AllowAny,)
    model = Network


class NetworkDetailAPIView(RetrieveAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = (NetworkDetailPermission,)
    model = Network