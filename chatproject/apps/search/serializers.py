# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User
from network.models import Network
from network.serializers import NetworkDetailAPISerializer
from search.models import SiteSearch


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'created_at', 'bio', 'avatar')
        read_only_fields = ('username', 'created_at', 'bio', 'avatar')


class VerySimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)
        read_only_fields = ('username',)


class SimpleNetworkSerializer(serializers.ModelSerializer):
    created_by = VerySimpleUserSerializer()

    class Meta:
        model = Network
        fields = ('name', 'created_by', 'slug')


read_only_field = ('name', 'created_by', 'slug')


class CombinedSearchResultSerializer(serializers.ModelSerializer):
    users = SimpleUserSerializer(many=True)
    networks = SimpleNetworkSerializer(many=True)

    class Meta:
        model = SiteSearch
        fields = ('users', 'networks', 'query')


