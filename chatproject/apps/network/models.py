# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from account.models import User
from django_extensions.db.fields import AutoSlugField
from core.managers import FilteringManager


class Network(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    # TODO: network silinince slugu update et
    slug = AutoSlugField(max_length=255, populate_from=('name',), unique=True)
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    is_deleted = models.BooleanField(_('Is deleted'), default=False)
    is_public = models.BooleanField(_('Is Public'), default=True)
    deleted_at = models.DateTimeField(_('Deleted Date'), null=True, blank=True)
    # managers
    objects = FilteringManager(is_deleted=False)
    public = FilteringManager(is_public=True, is_deleted=False)
    private = FilteringManager(is_public=False, is_deleted=False)

    class Meta:
        db_table = 'network'

    def __unicode__(self):
        return self.name

    def check_ownership(self, user):
        assert isinstance(User, user)
        assert User.actives.filter(id=user.id)
        return NetworkAdmin.objects.filter(user=user, network=self).exists()


class NetworkAdmin(models.Model):
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)

    MODERATOR = 'MOD'
    ADMIN = 'ADM'
    TYPE_CHOICES = ((MODERATOR, 'Moderator'), (ADMIN, 'Admin'))
    status = models.CharField(_('Type'), choices=TYPE_CHOICES, max_length=15)

    verbs = {
        'assigned': 'Network admin assigned',
    }

    class Meta:
        db_table = 'network_admin'

    def __unicode__(self):
        return "%s %s(%s) from %s" % (self.get_status_display(),
                                      self.user.username, self.user.id,
                                      self.network.name)


class NetworkConnection(models.Model):
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network, related_name='connection_set')
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    is_approved = models.BooleanField(_('Is Approved'))
    # objects
    objects = models.Manager()
    approved = FilteringManager(is_approved=True)

    class Meta:
        db_table = 'network_connection'

    def __unicode__(self):
        return "connection for %s(%s) to %s" % (self.user.username,
                                                self.user.id, self.network.name)

    @staticmethod
    def check_membership(user, network):
        # check types
        assert isinstance(user, User), u"Must be instance of User"
        assert isinstance(network, Network), u"Must be instance of Network"
        # user must be active
        if not User.actives.filter(id=user.id).exists():
            return False
        # network must not be deleted
        if not Network.objects.filter(id=network.id).exists():
            return False
        # finally check the connection
        return NetworkConnection.approved.filter(user=user,
                                                 network=network).exists()

