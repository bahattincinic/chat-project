from django.db import models
from rest_framework.authtoken.models import Token
from django.utils.translation import ugettext_lazy as _


class AccessToken(Token):
    is_deleted = models.BooleanField(_('Is Deleted'), default=False)
    deleted_at = models.DateTimeField(_('Deleted At'), null=True, blank=True)