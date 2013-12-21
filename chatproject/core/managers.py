from django.db import models
from .mixins import ManagerMixins, FilteringMixin


class CommonManager(models.Manager, ManagerMixins):
    pass


class FilteringManager(CommonManager, FilteringMixin):
    pass


class FilteringBaseManager(models.Manager, FilteringMixin):
    pass