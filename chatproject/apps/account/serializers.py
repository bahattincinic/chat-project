# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User, Report, Follow
from .validators import username_re
from django.contrib.auth import authenticate


class BaseUserSerializer(serializers.ModelSerializer):
    """
    Base User Serializer
    """
    followers = serializers.SerializerMethodField('followers_count')
    followees = serializers.SerializerMethodField('followees_count')
    username = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True,
                                           format='%d-%m-%Y %H:%M',)

    def followers_count(self, obj):
        return obj.followers().count()

    def followees_count(self, obj):
        return obj.followees().count()

    class Meta:
        abstract = True


class UserDetailSerializer(BaseUserSerializer):
    """
    User Detail, User Profile Update Serializer
    """

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
                  'last_notification_date', 'gender', 'followers', 'followees')


class AnonUserDetailSerializer(BaseUserSerializer):
    """
    Anon User Detail Serializer
    """

    class Meta:
        model = User
        fields = ('username', 'location', 'avatar', 'background',
                  'bio', 'gender', 'followers', 'followees')


class ForgotMyPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, attrs, source):
        email = attrs.get('email')
        user = User.objects.get_for_update_or_raise(
            email=email, exc=serializers.ValidationError('Email not found'))
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        return attrs

    def restore_object(self, attrs, instance=None):
        email = attrs.get('email')
        instance = User.objects.get(email=email)
        # fields pop
        self.fields.pop('email')
        return instance


class NewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    secret_key = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        secret_key = attrs.get('secret_key')
        user = User.objects.get_for_update_or_raise(
            email=email, secret_key=secret_key,
            exc=serializers.ValidationError('Email or secret code not found'))
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs

    def restore_object(self, attrs, instance=None):
        email = attrs.get('email')
        instance = User.objects.get(email=email)
        instance.set_password(attrs.get('new_password'))
        instance.secret_key = ''
        # fields pop
        self.fields.pop('email')
        self.fields.pop('secret_key')
        self.fields.pop('new_password')
        return instance


class UserRegister(serializers.ModelSerializer):
    """
    Create Account Serializer
    """
    email = serializers.EmailField(required=False)
    username = serializers.RegexField(
        required=True, regex=username_re,
        error_messages={'invalid': 'invalid username'})
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def validate_username(self, attrs, source):
        username = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('username this already exists')
        return attrs

    def validate_email(self, attrs, source):
        email = attrs.get('email', None)
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('E-Mail this already exists')
        return attrs

    def get_fields(self, *args, **kwargs):
        # encrypted password field clear
        fields = super(UserRegister, self).get_fields(*args, **kwargs)
        # fields pop
        fields.pop('password')
        return fields


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