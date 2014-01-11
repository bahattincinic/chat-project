from django.http.response import Http404
from rest_framework import permissions
from account.models import Follow, User


class UserDetailPermission(permissions.BasePermission):
    """
    User Detail or Update Permission
    """

    def has_permission(self, request, view):
        forbidden_methods = ('PUT', 'DELETE')
        if request.method in forbidden_methods:
            if request.user.is_authenticated():
                user = view.get_object()
                return request.user.username == user.username
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
            return request.user and request.user.is_anonymous()
        else:
            return False


class UserChangePasswordPermission(permissions.BasePermission):
    """
    User Change Password
    """
    def has_permission(self, request, view):
        if request.method == 'PUT':
            user = view.get_object()
            r_user = request.user
            return user.id == r_user.id
        else:
            return True


class FollowRelationPermissions(permissions.BasePermission):
    """
    User Followees, Followers Permission
    """
    def has_permission(self, request, view):
        if request.method == 'GET':
            user = view.get_object(queryset=view.queryset)
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
        username = request.parser_context.get("kwargs").get("username")
        user = User.objects.get_or_raise(username=username, exc=Http404())
        follow = Follow.objects.filter(follower=request.user, followee=user)
        if request.method == 'POST':
            if request.user.id == user.id:
                return False
            return not follow.exists()
        if request.method == 'DELETE':
            return follow.exists()
        return True


class UserCreateReportPermission(permissions.BasePermission):
    """
    User Create Report Permission
    """
    def has_permission(self, request, view):
        username = request.parser_context.get("kwargs").get("username")
        user = User.objects.get_or_raise(username=username, exc=Http404())
        if request.method == 'POST':
            return request.user.id != user.id
        if request.method == 'GET':
            return request.user.id == user.id
        return True


class UserReportDetailPermission(permissions.BasePermission):
    """
    User Report Detail Permission
    """
    def has_permission(self, request, view):
        user = view.get_object(queryset=view.queryset)
        r_user = request.user
        if request.method == 'GET':
            return request.user.is_authenticated() and r_user.id == user.id
        return True