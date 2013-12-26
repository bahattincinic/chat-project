from rest_framework import serializers
from account.models import User


class UserDetailSerializer(serializers.ModelSerializer):
    """
    User Detail, User Profile Update Serializer
    """
    username = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True,
                                           format='%d-%m-%Y %H:%M',)

    class Meta:
        model = User
        fields = ('username', 'email', 'created_at', 'location',
                  'avatar', 'background', 'is_sound_enabled', 'bio',
                  'follow_needs_approve', 'status',
                  'last_notification_date', 'gender')


class ForgotMyPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.get_for_update_or_raise(
            email=email, exc=serializers.ValidationError('Email not found'))
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
        attrs['user'] = user
        return attrs


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


class UserRegister(serializers.Serializer):
    """
    Create Account Serializer
    """
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_username(self, attrs, source):
        username = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('E-mail this already exists')
        return attrs

    def validate_email(self, attrs, source):
        email = attrs.get('email', None)
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('username this already exists')
        return attrs