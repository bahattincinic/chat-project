# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import uuid
from django.utils.timezone import utc
from django.conf import settings
from django.contrib.auth import login, logout
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from api.models import AccessToken
from actstream.models import action, Action
from account.models import User
from . import serializers
from . import permissions
from account.serializers import UserDetailSerializer


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = AccessToken.objects.get_or_create(
                user=serializer.object['user'], is_deleted=False)

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
                token.save()

            action.send(serializer.object['user'], verb=User.verbs.get("login"),
                        level=Action.INFO, type=settings.TOKEN_SESSION)
            user_data = UserDetailSerializer(serializer.object['user'])
            return Response({'user': user_data.data, 'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionAuthentication(APIView):
    serializer_class = AuthTokenSerializer
    permission_classes = (AllowAny,)
    model = User

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            login(request, serializer.object['user'])
            action.send(serializer.object['user'], verb=User.verbs.get("login"),
                        level=Action.INFO, type=settings.AUTH_SESSION)
            user_data = UserDetailSerializer(serializer.object['user'])
            return Response(user_data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionLogout(APIView):
    permission_classes = (IsAuthenticated,)
    model = User

    def get(self, request):
        user = request.user
        logout(request)
        action.send(user, verb=User.verbs.get('logout'), level=Action.INFO)
        return Response(status=status.HTTP_200_OK)


class TokenLogout(APIView):
    permission_classes = (IsAuthenticated,)
    model = User

    def get(self, request):
        auth = request.auth
        auth.is_deleted = True
        auth.deleted_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        auth.save()
        action.send(request.user, verb=User.verbs.get('logout'),
                    level=Action.INFO, action_object=auth,
                    auth_key=auth.key)
        return Response(status=status.HTTP_200_OK)


class ForgotPassword(generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    model = User
    serializer_class = serializers.ForgotMyPasswordSerializer

    def pre_save(self, obj):
        obj.secret_key = uuid.uuid4()

    def get_object(self, queryset=None):
        serializer = self.serializer_class(data=self.request.DATA)
        return serializer.object if serializer.is_valid() else None

    def post_save(self, obj, created=False):
        # Template
        template = get_template('email/forgot_password.html')
        template_context = Context({'user': obj, 'request': self.request})
        content = template.render(template_context)
        # log
        action.send(obj, verb=User.verbs.get('forgot_password'),
                    code='%s' % obj.secret_key, content=content,
                    level=Action.INFO)
        # mail send
        send_mail(subject="Forgot My Password", message=content,
                  recipient_list=[obj.email],
                  from_email=settings.DEFAULT_FROM_EMAIL)


class ForgotUsername(generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    model = User
    serializer_class = serializers.ForgotMyPasswordSerializer

    def get_object(self, queryset=None):
        serializer = self.serializer_class(data=self.request.DATA)
        return serializer.object if serializer.is_valid() else None

    def post_save(self, obj, created=False):
        # Template
        template = get_template('email/forgot_username.html')
        template_context = Context({'user': obj, 'request': self.request})
        content = template.render(template_context)
        # log
        action.send(obj, verb=User.verbs.get('forgot_username'),
                    content=content, level=Action.INFO)
        # mail send
        send_mail(subject="Forgot My Username", message=content,
                  recipient_list=[obj.email],
                  from_email=settings.DEFAULT_FROM_EMAIL)


class ForgotNewPassword(generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    model = User
    serializer_class = serializers.NewPasswordSerializer

    def get_object(self, queryset=None):
        serializer = self.serializer_class(data=self.request.DATA)
        return serializer.object if serializer.is_valid() else None

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('new_password'),
                    level=Action.INFO)


class AccountCreate(generics.CreateAPIView):
    permission_classes = (permissions.UserCreatePermission,)
    model = User
    serializer_class = serializers.UserRegister

    def pre_save(self, obj):
        # encrypted password set
        obj.set_password(obj.password)

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('register'), level=Action.INFO)
