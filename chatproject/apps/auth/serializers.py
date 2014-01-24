# -*- coding: utf-8 -*-
from rest_framework import serializers
from account.models import User
from account.validators import username_re


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

    def restore_object(self, attrs, instance=None):
        instance = super(UserRegister, self).restore_object(attrs, instance)
        self.fields.pop('password')
        return instance