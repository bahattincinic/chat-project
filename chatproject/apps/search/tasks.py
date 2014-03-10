import logging
import celery
from django.contrib.contenttypes.models import ContentType
from account.models import User
from network.models import Network
from account.search_indexes import UserSearchIndex
from network.search_indexes import NetworkSearchIndex


logger = logging.getLogger(__name__)

index_map = {
    'user': {'index': UserSearchIndex,
             'manager': User.actives},
    'network': {'index': NetworkSearchIndex,
                'manager': Network.objects}
}


def get_index(instance_id, ctype_id):
    ctype = ContentType.objects.get(id=ctype_id)
    index = index_map.get(ctype.name)
    if not index:
        raise Exception('failed to find index, invalid model')

    search_index = index.get('index')
    instance = index.get('manager').get(id=instance_id)
    return  search_index, instance


@celery.task(name='search.tasks.update', ignore_result=True,
             queue='haystack', retry=False)
def update(instance_id, ctype_id):
    try:
        search_index, instance = get_index(instance_id, ctype_id)
        search_index().update_object(instance)
    except Exception, e:
        logger.exception('Unable to update search index for %s(ct:%s), '
                         'error: %s' % (instance_id, ctype_id, e.message))

@celery.task(name='search.tasks.delete', ignore_result=True,
             queue='haystack', retry=False)
def remove(instance_id, ctype_id):
    try:
        search_index, instance = get_index(instance_id, ctype_id)
        search_index().remove_object(instance)
    except Exception, e:
        logger.exception('Unable to delete object from search index %s(ct:%s), '
                         'error: %s' % (instance_id, ctype_id, e.message))



@celery.task(name='search.tasks.reindex_all', ignore_result=True,
             queue='haystack', retry=False)
def reindex_all():
    print 'running update all'

