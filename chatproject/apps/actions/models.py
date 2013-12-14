# -*- coding: utf-8 -*-
import simplejson as json
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.conf import settings as base
from django.dispatch import Signal
from django.utils import timezone

action = Signal(
    providing_args=
    [
        'actor', 'level', 'verb', 'action_object',
        'target', 'description', 'timestamp'
    ])


class Action(models.Model):
    DEBUG = "0"
    INFO = "1"
    WARNING = "2"
    CRITICAL = "3"
    log_levels = ((DEBUG, "debug"),
                 (INFO, "info"),
                 (WARNING, "warning"),
                 (CRITICAL, "critical"))

    # who? optimized for Django 1.5 user model
    actor = models.ForeignKey(base.AUTH_USER_MODEL, related_name='actor')
    # log level
    level = models.CharField(choices=log_levels, max_length=2, default=INFO)
    # what happened?
    verb = models.CharField(max_length=255)
    # really, what happened?
    description = models.TextField(blank=True, null=True)
    # holds event more info in json data type, totally optional
    data = models.TextField(null=True, blank=True)
    # target_object, loosely coupled
    target_content_type = models.ForeignKey(ContentType, related_name='target',
        blank=True, null=True)
    target_object_id = models.CharField(max_length=255, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type',
        'target_object_id')
    # action_object loosely coupled
    action_object_content_type = models.ForeignKey(ContentType,
        related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(max_length=255, blank=True,
        null=True)
    action_object = generic.GenericForeignKey('action_object_content_type',
        'action_object_object_id')
    # when?
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return u"%s, level: %s" % (self.verb, self.level or Action.INFO)

    class Meta:
        ordering = ('-timestamp', )
        db_table = 'actions'

    @classmethod
    def action_handler(cls, sender, **kwargs):
        """
        Handler function to create Action instance upon action signal call.
        """
        kwargs.pop('signal', None)

        newaction = Action(
            actor=sender,
            verb=unicode(kwargs.pop('verb')),
            level=kwargs.pop('level', Action.INFO),
            description=kwargs.pop('description', None),
            timestamp=kwargs.pop('timestamp', timezone.now())
        )

        for opt in ('target', 'action_object'):
            obj = kwargs.pop(opt, None)
            if not obj is None:
                setattr(newaction, '%s_object_id' % opt, obj.pk)
                setattr(newaction, '%s_content_type' % opt,
                        ContentType.objects.get_for_model(obj))
        # store rest'of'em as json
        if len(kwargs):
            newaction.data = json.dumps(kwargs)
        newaction.save()

action.connect(Action.action_handler, dispatch_uid='action.models')
