# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haystack.inputs import Clean
from haystack.query import SearchQuerySet, SQ
from rest_framework import generics
from rest_framework.response import Response
from django.conf import settings
from account.models import User
from network.models import Network
from . import serializers
from .models import SiteSearch
from .permissions import SearchQueryPermission
from .tasks import save_search_query


class UserSearchAPIView(generics.RetrieveAPIView):
    model = SiteSearch
    serializer_class = serializers.CombinedSearchResultSerializer
    permission_classes = (SearchQueryPermission,)

    def retrieve(self, request, *args, **kwargs):
        query = Clean(self.request.QUERY_PARAMS.get('q'))
        limit = getattr(settings, "SEARCH_LIMIT", 5)
        users = SearchQuerySet().filter(SQ(username=query) | SQ(bio=query)).models(User)[:limit]
        networks = SearchQuerySet().filter(name=query).models(Network)[:limit]
        user_pks = [x.pk for x in users]
        network_pks = [x.pk for x in networks]
        users = User.actives.filter(id__in=user_pks)
        networks = Network.objects.select_related().filter(id__in=network_pks)
        data = {
            'users': serializers.SimpleUserSerializer(users, many=True).data,
            'networks': serializers.SimpleNetworkSerializer(networks, many=True).data,
            'query': query.query_string
        }
        save_search_query.delay(query=query.query_string,
                                user_ids=user_pks,
                                network_ids=network_pks)
        return Response(data)
