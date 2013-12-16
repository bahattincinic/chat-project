from django.db import models
from django.utils.translation import ugettext_lazy as _
from account.models import User


class Network(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=255)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    is_public = models.BooleanField(_('Is Public'), default=True)

    class Meta:
        db_table = 'network'


class NetworkAdmin(models.Model):
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)

    MODERATOR = 'moderator'
    ADMIN = 'admin'
    TYPE_CHOCIRIES = ((MODERATOR, 'Moderator'), (ADMIN, 'Admin'))
    admin_type = models.CharField(_('Type'), choices=TYPE_CHOCIRIES,
                                  max_length=15)

    class Meta:
        db_table = 'network_admin'


class NetworkConnection(models.Model):
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    is_approved = models.BooleanField(_('Is Approved'))
    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    deleted_at = models.DateTimeField(_('Deleted Date'), null=True, blank=True)

    class Meta:
        db_table = 'network_connection'