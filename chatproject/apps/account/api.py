# -*- coding: utf-8 -*-
from __future__ import absolute_import
import simplejson
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from actstream.models import action, Action
from account.models import User, Follow, Report
from . import serializers
from . import permissions
from core.generics import CreateDestroyAPIView
from core.mixins import ApiTransactionMixin


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
