import logging
import celery
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from account.models import User
from network.models import Network
from account.search_indexes import UserSearchIndex
from network.search_indexes import NetworkSearchIndex
from search.exceptions import SearchException


logger = logging.getLogger(__name__)

index_map = {
    'user': {'index': UserSearchIndex,
             'manager': User.vanilla},
    'network': {'index': NetworkSearchIndex,
                'manager': Network.vanilla},
}

index_ops = ('update', 'remove')

def get_index_metadata(instance_id, ctype_id):
    ctype = ContentType.objects.get(id=ctype_id)
    index = index_map.get(ctype.name)
    if not index:
        raise Exception('failed to find index, invalid model '
                        'to update search index')

    search_index = index.get('index')
    instance = index.get('manager').get(id=instance_id)
    return search_index, instance


@celery.task(name='search.tasks.update', ignore_result=True,
             queue='haystack', retry=False)
def update_index(instance_id, type_id, ops):
    try:
        if not ops in index_ops:
            raise SearchException('invalid operation submitted to worker')
        search_index, instance = get_index_metadata(instance_id, type_id)
        if ops == 'update':
            search_index().update_object(instance)
        elif ops == 'remove':
            search_index().remove_object(instance)
    except Exception, e:
        logger.exception('Unable to %s search index for %s(ct:%s), '
                         'error: %s' % (ops, instance_id, type_id, e.message))


@celery.task(name='search.tasks.reindex_all', ignore_result=True,
             queue='haystack', retry=False)
def reindex_all():
    for k,v in index_map.items():
        klass = v.get('index')
        klass().update()


@celery.task(name='search.tasks.record_search', ignore_result=True,
             queue='haystack', retry=False)
def save_search_query(query, user_ids, network_ids):
    from .models import SiteSearch

    if not query
    with transaction.atomic():
        s = SiteSearch.objects.create(query=query)
        users = User.actives.filter(id__in=user_ids)
        networks = Network.objects.filter(id__in=network_ids)
        for user in users:
            s.users.add(user)
        for n in networks:
            s.networks.add(n)
        s.save()


