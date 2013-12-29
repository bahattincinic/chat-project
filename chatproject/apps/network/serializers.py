# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Network


class NetworkAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network


class NetworkListAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ('id', 'name', 'created_at', 'is_public', 'slug')
