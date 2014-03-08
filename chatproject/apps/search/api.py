# -*- coding: utf-8 -*-
from __future__ import absolute_import
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from account.models import User
from account.serializers import UserDetailSerializer
from network.models import Network
from network.serializers import NetworkDetailAPISerializer


class UserSearchAPIView(generics.ListAPIView):
    model = User
    serializer_class = UserDetailSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return User.actives.filter(username='balkan')


class NetworkSearchAPIView(generics.ListAPIView):
    model = Network
    serializer_class = NetworkDetailAPISerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Network.public.all()

