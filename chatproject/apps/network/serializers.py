# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Network
from .models import NetworkConnection
from network.models import NetworkAdmin


class NetworkAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('id', 'name', 'created_at', 'is_public', 'slug')
        read_only_fields = ('id', 'created_at')


class NetworkDetailAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        read_only_fields = ('id', 'created_by', 'created_at',
                            'slug', 'is_deleted', 'deleted_at')


class NetworkConnectionAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkConnection
        fields = ('user', 'network')
        read_only_fields = ('user', 'network')


class NetworkAdminAPISerializer(serializers.ModelSerializer):
    network = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = NetworkAdmin
        fields = ('user', 'network')
