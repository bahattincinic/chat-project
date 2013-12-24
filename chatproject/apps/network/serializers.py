# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Network


class NetworkAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Network