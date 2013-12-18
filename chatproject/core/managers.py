from django.db import models


class FilteringManager(models.Manager):
    def __init__(self, **kwargs):
        self.filtering = kwargs
        return super(FilteringManager, self).__init__()

    def get_query_set(self):
        return super(FilteringManager, self).get_queryset()\
                                            .filter(**self.filtering)