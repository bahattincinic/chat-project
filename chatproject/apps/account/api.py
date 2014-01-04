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
from rest_framework.generics import (CreateAPIView, ListAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView, RetrieveAPIView)

from actstream.models import action, Action
from account.models import User, Follow, Report
from core.exceptions import OPSException
from api.models import AccessToken
from . import serializers
from .permissions import (UserCreatePermission, UserDetailPermission,
                          UserChangePasswordPermission,
                          UserFollowingsFollowersPermission,
                          UserAccountFollowPermission,
                          UserCreateReportPermission,
                          UserReportDetailPermission)
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


class ForgotMyPassword(ApiTransactionMixin, APIView):
    permission_classes = (AllowAny,)
    model = User

    def post(self, request):
        user = User.objects.none()
        content = ""
        data = None
        try:
            serializer = serializers.ForgotMyPasswordSerializer(
                data=request.DATA)
            if not serializer.is_valid():
                data = serializer.errors
                raise OPSException()
            # set secret key
            user = serializer.object.get('user')
            user.secret_key = uuid.uuid4()
            user.save()
            # Template
            template = get_template('email/forgot_my_password.html')
            template_context = Context({'user': user, 'request': request})
            content = template.render(template_context)
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            # log
            action.send(user, verb=User.verbs.get('forgot_password'),
                        code='%s' % user.secret_key, content=content,
                        level=Action.INFO)
            # mail send
            send_mail(subject="Forgot My Password", message=content,
                      recipient_list=[user.email],
                      from_email=settings.DEFAULT_FROM_EMAIL)
        return Response(data=data, status=statu)

    def put(self, request):
        user = User.objects.none()
        data = None
        try:
            serializer = serializers.NewPasswordSerializer(
                data=request.DATA)
            if not serializer.is_valid():
                data = serializer.errors
                raise OPSException()
            user = serializer.object.get('user')
            user.set_password(serializer.data.get('new_password'))
            user.secret_key = ''
            user.save()
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            action.send(user, verb=User.verbs.get('new_password'),
                        level=Action.INFO)
        return Response(data=data, status=statu)


class AccountCreate(ApiTransactionMixin, CreateAPIView):
    permission_classes = (UserCreatePermission,)
    model = User
    serializer_class = serializers.UserRegister

    def pre_save(self, obj):
        # encrypted password set
        obj.set_password(obj.password)

    def post_save(self, obj, created=False):
        action.send(obj, verb=User.verbs.get('register'), level=Action.INFO)


class AccountDetail(ApiTransactionMixin, RetrieveUpdateDestroyAPIView):
    permission_classes = (UserDetailPermission, UserChangePasswordPermission,)
    model = User
    serializer_class = serializers.UserDetailSerializer
    old_profile = None
    # request field <username>
    slug_url_kwarg = "username"
    # db field
    slug_field = "username"

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

    def patch(self, request, *args, **kwargs):
        data = None
        serializer = serializers.UserChangePasswordSerializer(data=request.DATA)
        try:
            if not serializer.is_valid():
                data = serializer.errors
                raise OPSException()
            user = request.user
            user.set_password(serializer.data.get('new_password'))
            user.save()
        except OPSException:
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            action.send(user, verb=User.verbs.get('password_update'))
        return Response(data=data, status=statu)


class AccountFollowers(ListAPIView):
    """
    User Followers
    """
    permission_classes = (UserFollowingsFollowersPermission, )
    serializer_class = serializers.AnonUserDetailSerializer
    model = User

    def get_queryset(self):
        username = self.kwargs.get('username')
        return User.objects.filter(follower_set__following__username=username)


class AccountFollowings(ListAPIView):
    """
    User Followings
    """
    permission_classes = (UserFollowingsFollowersPermission, )
    serializer_class = serializers.AnonUserDetailSerializer
    model = User

    def get_queryset(self):
        username = self.kwargs.get('username')
        return User.objects.filter(following_set__follower__username=username)


class AccountFollow(ApiTransactionMixin, APIView):
    """
    User Follow, UnFollow
    """
    model = User
    permission_classes = (UserAccountFollowPermission, )

    def post(self, request, *args, **kwargs):
        """
        User Follow
        """
        data = None
        try:
            username = kwargs.get('username')
            user = User.objects.get(username=username)
            control = Follow.objects.filter(follower=user,
                                            following=request.user)
            if control.exists():
                raise OPSException('User already follow')
            follow = Follow.objects.create(follower=user,
                                           following=request.user)
        except OPSException, e:
            data = {'username': e.message}
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_200_OK
            action.send(request.user, verb=Follow.verbs.get('follow'),
                        action_object=follow)
        return Response(data=data, status=statu)

    def delete(self, request, *args, **kwargs):
        """
        User UnFollow
        """
        data = None
        try:
            username = kwargs.get('username')
            user = User.objects.get(username=username)
            control = Follow.objects.filter(follower=user,
                                            following=request.user)
            if not control.exists():
                raise OPSException('user do not follow')
            control = control.get()
            # log
            following = control.following.username
            follower = control.follower.username
            # delete
            control.delete()
        except OPSException, e:
            data = {'username': e.message}
            statu = status.HTTP_400_BAD_REQUEST
        else:
            statu = status.HTTP_204_NO_CONTENT
            action.send(request.user, verb=Follow.verbs.get('unfollow'),
                        following=following, follower=follower)
        return Response(data=data, status=statu)


class AccountReportList(ApiTransactionMixin, ListCreateAPIView):
    """
    Account Report Create
    """
    model = Report
    queryset = Report.actives.all()
    serializer_class = serializers.UserReportSerializer
    permission_classes = (UserCreateReportPermission,)

    def pre_save(self, obj):
        username = self.kwargs.get('username')
        user = User.objects.get(username=username)
        obj.reporter = self.request.user
        obj.offender = user


class AccountReportDetail(RetrieveAPIView):
    """
    Account Report Detail
    """
    model = Report
    queryset = Report.actives.all()
    serializer_class = serializers.UserReportSerializer
    permission_classes = (UserReportDetailPermission, )
