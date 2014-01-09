# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import uuid
import simplejson
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

from actstream.models import action, Action
from account.models import User, Follow, Report
from core.exceptions import OPSException
from api.models import AccessToken
from . import serializers
from . import permissions
from core.generics import CreateDestroyAPIView
from core.mixins import ApiTransactionMixin


class ObtainExpiringAuthToken(ApiTransactionMixin, ObtainAuthToken):
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
            user_data = serializers.UserDetailSerializer(
                serializer.object['user'])
            return Response({'user': user_data.data, 'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionAuthentication(ApiTransactionMixin, APIView):
    serializer_class = AuthTokenSerializer
    permission_classes = (AllowAny,)
    model = User

    def post(self, request):
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            login(request, serializer.object['user'])
            action.send(serializer.object['user'], verb=User.verbs.get("login"),
                        level=Action.INFO, type=settings.AUTH_SESSION)
            user_data = serializers.UserDetailSerializer(serializer.object['user'])
            return Response(user_data.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionLogout(ApiTransactionMixin, APIView):
    permission_classes = (IsAuthenticated,)
    model = User

    def get(self, request):
        user = request.user
        logout(request)
        action.send(user, verb=User.verbs.get('logout'), level=Action.INFO)
        return Response(status=status.HTTP_200_OK)


class TokenLogout(ApiTransactionMixin, APIView):
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


class NewPassword(generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    model = User
    serializer_class = serializers.NewPasswordSerializer

    def get_object(self, queryset=None):
        serializer = self.serializer_class(data=self.request.DATA)
        return serializer.object if serializer.is_valid() else None

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('new_password'),
                    level=Action.INFO)


class AccountCreate(ApiTransactionMixin, generics.CreateAPIView):
    permission_classes = (permissions.UserCreatePermission,)
    model = User
    serializer_class = serializers.UserRegister

    def pre_save(self, obj):
        # encrypted password set
        obj.set_password(obj.password)

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('register'), level=Action.INFO)


class AccountDetail(ApiTransactionMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.UserDetailPermission, )
    model = User
    serializer_class = serializers.UserDetailSerializer
    old_profile = None
    lookup_field = "username"
    lookup_url_kwarg = "username"

    def get_serializer_class(self):
        if self.request.user.is_anonymous():
            return serializers.AnonUserDetailSerializer
        return serializers.UserDetailSerializer

    def pre_save(self, obj):
        self.old_profile = simplejson.dumps(
            self.serializer_class(instance=self.request.user).data)

    def post_save(self, obj, created=False):
        action.send(self.request.user, verb=User.verbs.get('update'),
                    level=Action.INFO, old_profile=self.old_profile)

    def post_delete(self, obj):
        # token logout
        tokens = obj.get_active_tokens()
        tokens.select_for_update().update(is_deleted=True)
        # session logout
        logout(self.request)
        # log
        action.send(obj, verb=User.verbs.get('delete'))


class AccountChangePassword(ApiTransactionMixin, generics.UpdateAPIView):
    model = User
    serializer_class = serializers.UserChangePasswordSerializer
    permission_classes = (IsAuthenticated,
                          permissions.UserChangePasswordPermission)
    lookup_field = "username"
    lookup_url_kwarg = "username"

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('password_update'))


class AccountFollowers(generics.ListAPIView):
    """
    User Followers
    """
    permission_classes = (IsAuthenticated,
                          permissions.FollowRelationPermissions, )
    serializer_class = serializers.AnonUserDetailSerializer
    model = User
    lookup_field = "username"
    lookup_url_kwarg = "username"
    queryset = User.actives.all()

    def get_queryset(self):
        user = self.get_object(queryset=self.queryset)
        return user.followers()


class AccountFollowees(generics.ListAPIView):
    """
    User Followees
    """
    permission_classes = (IsAuthenticated,
                          permissions.FollowRelationPermissions, )
    serializer_class = serializers.AnonUserDetailSerializer
    model = User
    lookup_field = "username"
    lookup_url_kwarg = "username"
    queryset = User.actives.all()

    def get_queryset(self):
        user = self.get_object(queryset=self.queryset)
        return user.followees()


class AccountFollow(ApiTransactionMixin, CreateDestroyAPIView):
    """
    User Follow, UnFollow
    /account/bahattincinic/follow/ -> (post)
        request.user bahattincinicí takip etmek istiyor
    """
    model = User
    permission_classes = (IsAuthenticated,
                          permissions.UserAccountFollowPermission, )
    serializer_class = serializers.UserFollowSerializer
    slug_field = "followee__username"
    slug_url_kwarg = "username"
    queryset = Follow.objects.all()

    def get_queryset(self):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        return Follow.objects.filter(followee=user, follower=self.request.user)

    def pre_save(self, obj):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        obj.followee = user
        obj.follower = self.request.user

    def post_save(self, obj, created=False):
        action.send(self.request.user, verb=Follow.verbs.get('follow'),
                    action_object=obj)

    def post_delete(self, obj):
        action.send(self.request.user, verb=Follow.verbs.get('unfollow'),
                    followee=obj.followee.username,
                    follower=obj.follower.username)


class AccountReportList(ApiTransactionMixin, generics.ListCreateAPIView):
    """
    Account Report Create
    """
    model = Report
    queryset = Report.actives.all()
    serializer_class = serializers.UserReportSerializer
    permission_classes = (IsAuthenticated,
                          permissions.UserCreateReportPermission,)

    def pre_save(self, obj):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        obj.reporter = self.request.user
        obj.offender = user


class AccountReportDetail(generics.RetrieveAPIView):
    """
    Account Report Detail
    """
    model = Report
    queryset = Report.actives.all()
    serializer_class = serializers.UserReportSerializer
    permission_classes = (permissions.UserReportDetailPermission, )
