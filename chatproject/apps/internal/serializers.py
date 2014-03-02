# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User


class UserTranslateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)
        read_only_fields = ('username',)