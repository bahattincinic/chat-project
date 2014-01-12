# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from account.models import User
from django_extensions.db.fields import AutoSlugField
from core.managers import FilteringManager, CommonManager


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
        """
        Checks if user is creator and admin of this network
        """
        assert isinstance(user, User)
        assert User.actives.filter(id=user.id).exists()
        admin = NetworkAdmin.objects.get(network=self, status=NetworkAdmin.ADMIN).user
        return admin.id == user.id


class NetworkAdmin(models.Model):
    """
    Administration rights
    if ADMIN then creator of this network
    if MODERATOR then user appointed by admin
    """
    # type of this connection
    ADMIN = 'ADM'
    MODERATOR = 'MOD'
    TYPE_CHOICES = ((MODERATOR, 'Moderator'), (ADMIN, 'Admin'))
    status = models.CharField(_('Type'), choices=TYPE_CHOICES, max_length=4)
    # which user
    user = models.ForeignKey(User)
    # which network
    network = models.ForeignKey(Network, related_name='admin_set')
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    connection = models.OneToOneField('NetworkConnection')

    verbs = {
        'assigned': 'Network admin assigned',
    }

    objects = CommonManager()

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
    # managers
    approved = FilteringManager(is_approved=True)
    objects = models.Manager()

    class Meta:
        db_table = 'network_connection'

    def __unicode__(self):
        return "%s NetworkConnection '%s' to '%s'" % ('Approved' if self.is_approved else 'Awaiting',
                                                      self.user.username,
                                                      self.network.name)

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

