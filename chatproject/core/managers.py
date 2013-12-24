# -*- coding: utf-8 -*-
from django.db import models
from .mixins import ManagerMixins, FilteringMixin


class CommonManager(models.Manager, ManagerMixins):
    pass


class FilteringManager(FilteringMixin, CommonManager):
    pass


class FilteringBaseManager(models.Manager, FilteringMixin):
    pass