# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Page


class PageAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        exclude = ('is_active', 'id')
        read_only_fields = ('slug', 'name', 'description', 'summary')

