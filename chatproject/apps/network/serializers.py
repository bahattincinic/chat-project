# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Network
from .models import NetworkConnection


class NetworkAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('id', 'name', 'created_at', 'is_public', 'slug')
        read_only_fields = ('id', 'created_at')


class NetworkDetailAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network


class NetworkConnectionAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkConnection
        fields = ('user', 'network')
        read_only_fields = ('user', 'network')
