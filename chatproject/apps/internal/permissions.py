import logging
from rest_framework.permissions import BasePermission
from django.conf import settings

logger = logging.getLogger(__name__)

class LocalPermission(BasePermission):
    def has_permission(self, request, view):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        if not str(ip) in settings.INTERNAL_ALLOWED:
            logger.error("Deny ip: %s from reaching internal api" % str(ip))
            return False
        return True