from django.contrib.contenttypes.models import ContentType
import logging
from haystack import signals
from account.models import User
from network.models import Network
from search.tasks import update, remove
from .exceptions import SearchException

logger = logging.getLogger(__name__)

class QueuedSignalProcessor(signals.RealtimeSignalProcessor):
    @classmethod
    def get_ctype_id(cls, instance):
        if not isinstance(instance, (User, Network)):
            raise SearchException('Invalid object type to update search index')
        return ContentType.objects.get_for_model(instance).id

    def handle_save(self, sender, instance, **kwargs):
        try:
            ctype_id = self.get_ctype_id(instance)
            update.delay(instance.id, ctype_id)
        except SearchException, e:
            logger.error('Not updating search index: %s' % e.message)

    def handle_delete(self, sender, instance, **kwargs):
        try:
            ctype_id = self.get_ctype_id(instance)
            remove.delay(instance.id, ctype_id)
        except SearchException, e:
            logger.error('Not updating search index: %s' % e.message)


