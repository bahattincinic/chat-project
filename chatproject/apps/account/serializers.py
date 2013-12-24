# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'created_at', 'location',
                  'avatar', 'background', 'is_sound_enabled', 'bio',
                  'follow_needs_approve', 'status',
                  'last_notification_date', 'gender')