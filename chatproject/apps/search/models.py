from django.db import models
from account.models import User
from network.models import Network


class SearchQuery(models.Model):
    users = models.ManyToManyField(User)
    networks = models.ManyToManyField(Network)
    query = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "queried: %s" % self.query

