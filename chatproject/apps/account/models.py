# -*- coding: utf-8 -*-
import re

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.db import models
from .managers import UserManager
from core.managers import CommonManager, FilteringManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'), 'invalid')
        ])
    email = models.EmailField(_('email address'), blank=True)
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    created_at = models.DateTimeField(_('date joined'), auto_now_add=True)
    location = models.CharField(_('Location'), max_length=100,
                                null=True, blank=True)
    # TODO: /media/avatar/bahattincinic/hede.png seklinde olucak
    avatar = models.ImageField(_('Avatar'), upload_to='avatar/',
                               null=True, blank=True)
    background = models.ImageField(_('Backgroud'), upload_to='background/',
                                   null=True, blank=True)
    is_sound_enabled = models.BooleanField(_('Chat Sound'), default=True)
    bio = models.CharField(_('Biography'), max_length=255,
                           null=True, blank=True)

    CHAT_ACTIVE = 'ACTIVE'
    CHAT_PASSIVE = 'PASSIVE'
    CHAT_FOLLOWS_ONLY = 'FOLLOWS_ONLY'
    STATUS_CHOICES = ((CHAT_ACTIVE, 'Chat Active'),
                        (CHAT_PASSIVE, 'Chat Passive'),
                        (CHAT_FOLLOWS_ONLY, 'Follows Only'))

    follow_needs_approve = models.BooleanField(default=False)

    status = models.CharField(_('Status'), choices=STATUS_CHOICES,
                              default=CHAT_ACTIVE, max_length=10)
    is_deleted = models.BooleanField(_('Deleted'), default=False)
    last_notification_date = models.DateTimeField(_('Last Notification'),
                                                  null=True, blank=True)
    secret_key = models.CharField(_('Secret Key'), max_length=255,
                                  null=True, blank=True)

    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    GENDER_CHOICES = ((MALE, 'Male'), (FEMALE, 'Female'), (OTHER, 'Other'))
    gender = models.CharField(_('Gender'), choices=GENDER_CHOICES,
                              null=True, blank=True, max_length=10)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager(is_deleted=False)
    actives = UserManager(is_deleted=False, is_active=True)

    verbs = {
        'login': 'Login',
        'logout': 'Logout',
        'register': 'Register',
    }

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'user'

    @staticmethod
    def get_logger():
        logger, _ = User.objects.get_or_create(username="logger")
        return logger

    def __unicode__(self):
        return "%s(%s)" % (self.username, self.id)

    def get_full_name(self):
        full_name = '%s <%s>' % (self.username, self.email)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.username


class Follow(models.Model):
    following = models.ForeignKey(User, related_name='following_set')
    follower = models.ForeignKey(User, related_name='follower_set')
    created_at = models.DateTimeField(_('Follow Created'), auto_now_add=True)

    objects = CommonManager()

    # TODO: follow, unfollow log atilmasi lazim
    class Meta:
        db_table = 'user_follow'

    def __unicode__(self):
        return "%s following %s  since %s" % (self.follower.username,
                                              self.following.username,
                                              self.created_at)


class Report(models.Model):
    reporter = models.ForeignKey(User, related_name='reporter_set')
    offender = models.ForeignKey(User, related_name='offender_set')
    created_at = models.DateTimeField(_('Report Created'), auto_now_add=True)

    ACTIVE = 'active'
    PASSIVE = 'passive'
    RESOLVED = 'resolved'
    STATUS_CHOCIRIES = ((ACTIVE, 'Active'), (PASSIVE, 'Passive'),
                        (RESOLVED, 'Resolved'))
    status = models.CharField(_('Status'), choices=STATUS_CHOCIRIES,
                              max_length=10)
    text = models.TextField(_('Other/Text'), null=True, blank=True)

    objects = CommonManager()

    class Meta:
        db_table = 'user_report'

    def __unicode__(self):
        return "Report about %s by %s when %s" % (self.offender.username,
                                                  self.reporter.username,
                                                  self.created_at)