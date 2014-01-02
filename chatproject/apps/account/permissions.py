from django.http.response import Http404
from rest_framework import permissions
from account.models import User


class UserDetailPermission(permissions.BasePermission):
    """
    User Detail or Update Permission
    """

    def has_permission(self, request, view):
        forbidden_methods = ('PUT', 'DELETE')
        if request.method in forbidden_methods:
            if request.user.is_authenticated():
                username = request.parser_context.get("kwargs").get("username")
                user = User.objects.get_or_raise(username=username,
                                                 exc=Http404())
                if request.user.username == user.username:
                    return True
                return False
            else:
                return False
        else:
            return True


class UserCreatePermission(permissions.BasePermission):
    """
    User Register Permission
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            if request.user and request.user.is_anonymous():
                return True
            return False
        else:
            return False


class UserChangePasswordPermission(permissions.BasePermission):
    """
    User Change Password
    """
    def has_permission(self, request, view):
        if request.method == 'PATCH':
            if request.user.is_authenticated():
                return True
            else:
                return False
        else:
            return True


class UserFollowingsFollowersPermission(permissions.BasePermission):
    """
    User Followings, Followers Permission
    """
    def has_permission(self, request, view):
        username = request.parser_context.get("kwargs").get("username")
        user = User.objects.get_or_raise(username=username, exc=Http404())
        if request.method == 'GET':
            if request.user.is_anonymous():
                return False
            if request.user.username != user.username:
                return False
            return True
        else:
            return True


class UserAccountFollowPermission(permissions.BasePermission):
    """
    User Follow, UnFollow Permission
    """
    def has_permission(self, request, view):
        forbidden_methods = ('POST', 'DELETE')
        username = request.parser_context.get("kwargs").get("username")
        user = User.objects.get_or_raise(username=username, exc=Http404())
        if request.method in forbidden_methods:
            if request.user.is_authenticated():
                # User can not follow self
                if request.user.username == user.username:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True