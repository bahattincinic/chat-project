from rest_framework import permissions
from account.models import User


class UserDetailPermission(permissions.BasePermission):
    """
    User Detail or Update Permission
    """

    def has_permission(self, request, view):
        safe_methods = ('PUT', 'DELETE')
        if request.method in safe_methods and request.user.is_authenticated():
            username = request.parser_context.get("kwargs").get("username")
            user = User.objects.get(username=username)
            if request.user.username == user.username:
                return True
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