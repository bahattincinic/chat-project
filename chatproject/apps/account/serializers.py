# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User, Report, Follow
from django.conf import settings


class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base User Serializer
    """
    followers = serializers.SerializerMethodField('followers_count')
    followees = serializers.SerializerMethodField('followees_count')
    session = serializers.SerializerMethodField('session_count')
    avatar_url = serializers.SerializerMethodField('avatar_path')
    background_url = serializers.SerializerMethodField('background_path')
    username = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True,
                                           format='%d-%m-%Y %H:%M',)

    def followers_count(self, obj):
        return obj.followers().count()

    def followees_count(self, obj):
        return obj.followees().count()

    def session_count(self, obj):
        return obj.chatsession_set.count()

    def background_path(self, obj):
        return '%s%s' % (settings.BACKGROUND_MEDIA_URL, obj.background)

    def avatar_path(self, obj):
        return '%s%s' % (settings.AVATAR_MEDIA_URL, obj.avatar)

    class Meta:
        abstract = True


class UserDetailSerializer(BaseUserSerializer):
    """
    User Detail, User Profile Update Serializer
    """
    avatar = serializers.ImageField(required=False)
    background = serializers.ImageField(required=False)

    def validate(self, attrs):
        user = self.context['view'].request.user
        if isinstance(user, User) and user.email != attrs.get('email'):
            if User.objects.filter(email=attrs.get('email')).exists():
                raise serializers.ValidationError('email is used')
        return attrs

    class Meta:
        model = User
        fields = ('username', 'email', 'created_at', 'location',
                  'avatar', 'background', 'is_sound_enabled', 'bio',
                  'follow_needs_approve', 'status',
                  'last_notification_date', 'gender',
                  'followers', 'followees', 'session',
                  'avatar_url', 'background_url')


class AnonUserDetailSerializer(BaseUserSerializer):
    """
    Anon User Detail Serializer
    """

    class Meta:
        model = User
        fields = ('username', 'location', 'avatar', 'background',
                  'bio', 'gender', 'followers', 'followees', 'session',
                  'avatar_url', 'background_url')


class UserChangePasswordSerializer(serializers.Serializer):
    """
    Account New Password
    """
    password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password', None)
        confirm_password = attrs.get('confirm_password', None)
        if new_password and confirm_password:
            if new_password == confirm_password:
                return attrs
            else:
                raise serializers.ValidationError('passwords did not match')
        else:
            raise serializers.ValidationError('passwords did not match')

    def validate_password(self, attrs, source):
        password = attrs.get('password')
        user = self.context['view'].request.user
        if not user.is_authenticated():
            raise serializers.ValidationError("user not authenticated")
        if not user.check_password(password):
            raise serializers.ValidationError('passwords invalid')
        return attrs

    def restore_object(self, attrs, instance=None):
        user = self.context['view'].request.user
        if not user.is_authenticated():
            raise serializers.ValidationError("user not authenticated")
        # change password
        instance = user
        instance.set_password(attrs.get('new_password'))
        # fields pop
        self.fields.pop('new_password')
        self.fields.pop('confirm_password')
        self.fields.pop('password')
        return instance


class UserReportSerializer(serializers.ModelSerializer):
    """
    Account Report Serializer
    """
    reporter = AnonUserDetailSerializer(read_only=True)
    offender = AnonUserDetailSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'reporter', 'offender', 'text')
        read_only_fields = ('id',)


class UserFollowSerializer(serializers.ModelSerializer):

    followee = AnonUserDetailSerializer(read_only=True)
    follower = AnonUserDetailSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('followee', 'follower')