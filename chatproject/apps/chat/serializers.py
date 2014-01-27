# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import AnonUser, ChatMessage, ChatSession
from account.serializers import AnonUserDetailSerializer as UserSerializer


class AnonUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnonUser
        exclude = ('id', 'is_registered_user', 'started_by',
                   'created_at', 'device', 'last_modified_at',)
        read_only_fields = ('username', )


class SessionSerializer(serializers.ModelSerializer):
    target = UserSerializer(read_only=True)
    anon = AnonUserSerializer(read_only=True)

    class Meta:
        model = ChatSession
        fields = ('target', 'anon', 'uuid')
        read_only_fields = ('uuid',)


class MessageSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('content', 'session', 'direction')
        read_only_fields = ('direction',)


class SessionMessageSerializer(serializers.ModelSerializer):
    message_set = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        exclude = ('id', 'created_at', 'last_message_at', 'uuid')
        read_only_fields = ('uuid',)