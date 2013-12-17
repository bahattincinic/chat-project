# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
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

    ACTIVE = 'ACT'
    PASSIVE = 'PASS'
    STATUS_CHOICES = ((ACTIVE, 'Active'), (PASSIVE, 'Passive'))
    status = models.CharField(_('Status'), choices=STATUS_CHOICES,
                              max_length=20)

    class Meta:
        db_table = 'chat_session'

    def __unicode__(self):
        return "ChatSession with  %s (%s) " \
               "as target an %s(%s) as anon user " \
               "created_at %s" % (self.target.username, self.target.id,
                                  self.anon.username, self.anon.id,
                                  self.created_at)


class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession)

    TO_USER = 'TO_USR'
    TO_ANON = 'TO_ANON'
    DIRECTION = ((TO_USER, 'From Anon to User'), (TO_ANON, 'From User to Anon'))
    direction = models.CharField(max_length=8, choices=DIRECTION)

    content = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created Date'), auto_now_add=True)

    device = models.CharField(_('Device Type'),
                              choices=settings.DEVICE_CHOCIES,
                              max_length=20)

    class Meta:
        db_table = 'chat_message'

    @property
    def author(self):
        if self.direction == self.TO_ANON:
            return self.session.target
        else:
            return self.session.anon

    @property
    def recipient(self):
        if self.direction == self.TO_ANON:
            return self.session.anon
        else:
            return self.session.target

    def __unicode__(self):
        return "ChatMessage with user %s(%s)" \
               "and anon %s(%s)" % (self.session.target.username,
                                    self.session.target.id,
                                    self.session.anon.username,
                                    self.session.anon.id)