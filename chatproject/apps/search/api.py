# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haystack.inputs import Clean
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from account.models import User
from account.serializers import UserDetailSerializer
from network.models import Network
from network.serializers import NetworkDetailAPISerializer
from .serializers import CombinedSearchResultSerializer


class UserSearchAPIView(generics.ListAPIView):
    model = User
    serializer_class = UserDetailSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        print self.kwargs
        query = self.request.QUERY_PARAMS.get('q')
        if not query:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        query = Clean(query)
        return User.actives.filter(username='balkan')


class NetworkSearchAPIView(generics.ListAPIView):
    model = Network
    serializer_class = NetworkDetailAPISerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Network.public.all()


class SearchAPIView(generics.ListAPIView):
    serializer_class = CombinedSearchResultSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Network.objects.all()

