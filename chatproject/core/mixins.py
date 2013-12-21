from django.db.models.query import QuerySet
from core.exceptions import OPSException


class ManagerMixins(object):
    def get_or_raise(self, exc=OPSException("Instance not found"), **kwargs):
        instance = self.filter(**kwargs)
        if not instance.count() == 1:
            raise exc
        return instance.get()

    def get_for_update_if_exists(self, **kwargs):
        instance = self.filter(**kwargs)
        if not instance.count() == 1:
            return None, False
        instance = self.select_for_update().filter(**kwargs)
        return instance.get(), True

    def get_for_update_or_raise(self, exc=OPSException("Instance not found"),
                                **kwargs):
        instance = self.select_for_update().filter(**kwargs)
        if not instance.count() == 1:
            raise exc
        return instance.get()

    def get_if_exists(self, **kwargs):
        instance = self.filter(**kwargs)
        if instance.count() == 1:
            return instance.get(), True
        return None, False


class FilteringMixin(object):
    def __init__(self, **filter_options):
        self.clause = filter_options

    def get_query_set(self):
        """
        Mixin class for default filtering
        when creating a QuerySet
        """
        return QuerySet(self.model, using=self._db).filter(**self.clause)
