# -*- coding: utf-8 -*-
from django.db import models
from django_extensions.db.fields import AutoSlugField
from core.managers import FilteringManager, CommonManager


class Page(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name',))
    summary = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = CommonManager()
    actives = FilteringManager(is_active=True)

    def __unicode__(self):
        return "%s %s" % (self.id, self.name)

