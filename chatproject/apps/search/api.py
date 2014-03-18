# -*- coding: utf-8 -*-
from __future__ import absolute_import
import simplejson as json
from haystack.inputs import Clean
from haystack.query import SearchQuerySet, SQ
from rest_framework import generics
from rest_framework.response import Response
from django.conf import settings
from account.models import User
from network.models import Network
from .serializers import CombinedSearchResultSerializer
from .models import SiteSearch
from .permissions import SearchQueryPermission


class UserSearchAPIView(generics.RetrieveAPIView):
    model = SiteSearch
    serializer_class = CombinedSearchResultSerializer
    permission_classes = (SearchQueryPermission,)

    # def retrieve(self, request, *args, **kwargs):
    #     query = Clean(self.request.QUERY_PARAMS.get('q'))
    #     limit = getattr(settings, "SEARCH_LIMIT", 5)
    #     users = SearchQuerySet().filter(SQ(username=query) | SQ(bio=query)).models(User)[:limit]
    #     networks = SearchQuerySet().filter(name=query).models(Network)[:limit]
    #     user_pks = [x.pk for x in users]
    #     network_pks = [x.pk for x in networks]
    #     search_query = SiteSearch.objects.create(query=query)
    #     [search_query.users.add(u) for u in User.actives.filter(id__in=user_pks)]
    #     [search_query.networks.add(u) for u in Network.objects.filter(id__in=network_pks)]
    #     return Response(json.dumps({}))

    def get_object(self, queryset=None):
        query = Clean(self.request.QUERY_PARAMS.get('q'))
        limit = getattr(settings, "SEARCH_LIMIT", 5)
        users = SearchQuerySet().filter(SQ(username=query) | SQ(bio=query)).models(User)[:limit]
        networks = SearchQuerySet().filter(name=query).models(Network)[:limit]
        user_pks = [x.pk for x in users]
        network_pks = [x.pk for x in networks]
        search_query = SiteSearch.objects.create(query=query)
        [search_query.users.add(u) for u in User.actives.filter(id__in=user_pks)]
        [search_query.networks.add(u) for u in Network.objects.filter(id__in=network_pks)]
        return search_query
