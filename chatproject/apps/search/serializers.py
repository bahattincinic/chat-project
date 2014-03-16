# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User
from network.serializers import NetworkDetailAPISerializer
from search.models import SearchQuery


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'avatar')


class CombinedSearchResultSerializer(serializers.ModelSerializer):
    users = SimpleUserSerializer(many=True)
    networks = NetworkDetailAPISerializer(many=True)

    class Meta:
        model = SearchQuery
        fields = ('users', 'networks', 'query')