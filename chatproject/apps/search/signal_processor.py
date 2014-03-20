from django.contrib.contenttypes.models import ContentType
from django.db import models
import logging
from haystack import signals
from account.models import User
from network.models import Network
from search.tasks import update_index
from .exceptions import SearchException

logger = logging.getLogger(__name__)


class QueuedSignalProcessor(signals.RealtimeSignalProcessor):
    indexed_models = (User, Network)
    def setup(self):
        for model in self.indexed_models:
            models.signals.post_save.connect(sender=model, receiver=self.handle_save)
            models.signals.post_delete.connect(sender=Network, receiver=self.handle_delete)

    def teardown(self):
        for model in self.indexed_models:
            models.signals.post_save.disconnect(sender=model, receiver=self.handle_delete)
            models.signals.post_delete.disconnect(sender=model, receiver=self.handle_delete)

    @classmethod
    def get_type_id(cls, instance):
        if not isinstance(instance, (User, Network)):
            raise SearchException('Invalid object type to update search index')
        return ContentType.objects.get_for_model(instance).id

    def handle_save(self, sender, instance, **kwargs):
        if hasattr(instance, 'is_deleted') and instance.is_deleted:
            # not updating deleted instance
            return

        try:
            type_id = self.get_type_id(instance)
            update_index.delay(instance_id=instance.id,
                               type_id=type_id,
                               ops='update')
        except SearchException, e:
            logger.error('Not updating search index: %s' % e.message)

    def handle_delete(self, sender, instance, **kwargs):
        try:
            type_id = self.get_type_id(instance)
            update_index.delay(instance_id=instance.id,
                               type_id=type_id,
                               ops='remove')
        except SearchException, e:
            logger.error('Not updating search index: %s' % e.message)


