# -*- coding: utf-8 -*-
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .permissions import PrivateNetworkPermission, PublicNetworkPermission
from .serializers import NetworkAPISerializer
from .models import Network


class NetworkAPIView(ListAPIView):
    serializer_class = NetworkAPISerializer
    permission_classes = \
        (PublicNetworkPermission, PrivateNetworkPermission)
    # permission_classes = (AllowAny, )
    model = Network


