from rest_framework import permissions


class UserDetailPermission(permissions.BasePermission):
    """
    User Detail or Update Permission
    """

    def has_permission(self, request, view):
        safe_methods = ['GET', 'PUT', 'DELETE']
        if request.method in safe_methods:
            if request.user and request.user.is_authenticated():
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
            return True