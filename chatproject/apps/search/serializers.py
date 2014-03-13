# -*- coding: utf-8 -*-
from rest_framework import serializers
from network.serializers import NetworkAPISerializer
from account.serializers import UserDetailSerializer
from account.models import User


class CombinedSearchResultSerializer(serializers.Serializer):
    network = NetworkAPISerializer(many=True)
    user = UserDetailSerializer(many=True)


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'created_at')