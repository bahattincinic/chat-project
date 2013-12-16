# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from account.models import User
from django.conf import settings
from django.utils import timezone


class AnonUser(models.Model):
    u"""Anonim kullanıcıların kayıtlı kullanıcılara mesaj atacak olan kullanıcı
    """
    # TODO: otomatik olarak oluşturulacak, Anon-xxxxx
    username = models.CharField(_('Username'), max_length=64, unique=True)
    started_by = models.ForeignKey(User, null=True, blank=True)
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)
    is_registered_user = models.BooleanField(default=False)
    device = models.CharField(_('Device'), choices=settings.DEVICE_CHOCIES,
                              max_length=20)
    last_modified_at = models.DateTimeField(_('Last Modified Date'),
                                            auto_now=True)

    class Meta:
        db_table = 'chat_anonuser'

    @property
    def recorded_username(self):
        if self.is_registered_user:
            return self.started_by.username
        else:
            return 'Anon User'

    def __unicode__(self):
        return "%s(%s)  %s" % (self.username, self.recorded_username,
                               self.created_at)


class ChatSession(models.Model):
    target = models.ForeignKey(User)
    anon = models.ForeignKey(AnonUser)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    last_message_at = models.DateTimeField(_('Last Update Date'),
                                           default=timezone.now())

    ACTIVE = 'active'
    PASSIVE = 'passive'
    STATUS_CHOCIRIES = ((ACTIVE, 'Active'), (PASSIVE, 'Passive'))
    status = models.CharField(_('Status'), choices=STATUS_CHOCIRIES,
                              max_length=20)

    target_type = models.CharField(_('Target Type'),
                                   choices=settings.DEVICE_CHOCIES,
                                   max_length=20)

    class Meta:
        db_table = 'chat_session'


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession)

    from_content_type = models.ForeignKey(ContentType,
                                          related_name='from_contenttype')
    to_content_type = models.ForeignKey(ContentType,
                                        related_name='to_contenttype')

    from_object_id = models.PositiveIntegerField()
    to_object_id = models.PositiveIntegerField()

    to_content_object = generic.GenericForeignKey(
        'to_content_type', 'to_object_id')
    from_content_object = generic.GenericForeignKey(
        'from_content_type', 'from_object_id')

    content = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)

    device = models.CharField(_('Device Type'),
                              choices=settings.DEVICE_CHOCIES,
                              max_length=20)

    class Meta:
        db_table = 'chat_message'