# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.http.response import Http404
from rest_framework import generics
from . import serializers
from . import permissions
from rest_framework.permissions import AllowAny
from account.models import User
from chat.models import ChatSession, AnonUser, ChatMessage
from utils import SAFE_METHODS


class SessionAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.SessionSerializer
    permission_classes = (
        permissions.IsPostOrActiveAuthenticated,
        permissions.IsRequestingUserDiffThanUrl,
    )
    model = ChatSession

    def get_queryset(self):
        return ChatSession.objects.filter(target=self.request.user)

    def pre_save(self, obj):
        obj.anon = AnonUser.create_anon_user(self.request.user,
                                             device='desktop')
        username = self.kwargs.get('username')
        target = User.actives.get_or_raise(username=username,
                                           exc=Http404())
        obj.target = target

    def post_save(self, obj, created=False):
        # TODO: redis/nodejs baglantisi ve log
        pass


class SessionDetailAPIView(generics.RetrieveAPIView):
    model = ChatSession
    serializer_class = serializers.SessionSerializer
    permission_classes = (
        permissions.IsPostOrActiveAuthenticated,
        permissions.IsPostOrRequestingUserMatchesUsername,
    )
    lookup_field = 'uuid'


class SessionMessageAPIView(generics.ListCreateAPIView):
    model = ChatMessage
    serializer_class = serializers.MessageSerializer
    permission_classes = (
        permissions.IsPostOrRequestingUserMatchesUsername,
        permissions.IsPostOrActiveAuthenticated,
    )

    def pre_save(self, obj):
        uuid = self.kwargs.get('uuid')
        username = self.kwargs.get('username')
        # TODO: get direction in here
        user = User.actives.get_or_raise(username=username,
                                         exc=Http404())
        session = ChatSession.objects.get_or_raise(uuid=uuid,
                                                   target=user,
                                                   exc=Http404())
        obj.session = session

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.SessionMessageSerializer
        return serializers.MessageSerializer

    def get_queryset(self):
        uuid = self.kwargs.get('uuid')
        user = self.request.user
        return ChatSession.objects.get(uuid=uuid, target=user)