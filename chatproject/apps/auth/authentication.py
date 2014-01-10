from __future__ import absolute_import
import datetime

from django.utils.timezone import utc
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.conf import settings
from api.models import AccessToken


class ExpiringTokenAuthentication(TokenAuthentication):
    model = AccessToken

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key, is_deleted=False)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        utc_now = datetime.datetime.utcnow().replace(tzinfo=utc)

        if token.created < utc_now - datetime.timedelta(
                days=settings.API_TOKEN_TTL):
            raise exceptions.AuthenticationFailed('Token has expired')

        return token.user, token