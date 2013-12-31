# -*- coding: utf-8 -*-
from django.db import models
from .mixins import ManagerMixins, FilteringMixin


class CommonManager(models.Manager, ManagerMixins):
    pass


class FilteringManager(FilteringMixin, CommonManager):
    def __init__(self, **filter_options):
        FilteringMixin.__init__(self, **filter_options)
        CommonManager.__init__(self)


class FilteringBaseManager(FilteringMixin, models.Manager):
    def __init__(self, **filter_options):
        FilteringMixin.__init__(self, **filter_options)
        models.Manager.__init__(self)